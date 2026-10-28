#!/usr/bin/env bash
# Sourced by the launcher. Values are data, never evaluated as shell code.
image_source=local
image_namespace=''
release_version=1.0.0
image_tag="$release_version"
image_source_explicit=0
image_tag_explicit=0
image_arch=''
image_layout=manifest
image_layout_explicit=0
resolved_latest_image_id=''

validate_image_selection() {
  case "$image_source" in local | hub) ;; *) fail 'Image source must be local or hub.' ;; esac
  case "$image_layout" in manifest | architecture) ;; *) fail 'Unknown published image layout.' ;; esac
  if [ "$image_tag" = latest ]; then
    if [ "${1:-resolved}" != pending ] || [ "$image_source_explicit" -eq 1 ]; then
      [ "$image_source" = hub ] && [ "$image_layout" = manifest ] || fail 'latest is available only for multi-platform Docker Hub releases.'
    fi
  else
    [[ "$image_tag" =~ ^[0-9]+\.[0-9]+\.[0-9]+([.-][a-zA-Z0-9][a-zA-Z0-9.-]*)?$ ]] || fail 'Use a release version, or latest with --from-hub.'
  fi
  if [ "$image_source" = hub ]; then
    [[ "$image_namespace" =~ ^[a-z0-9][a-z0-9_-]{1,38}$ ]] || fail 'Use a Docker Hub username or organization, without a URL, password or slash.'
  else
    [ -z "$image_namespace" ] || fail 'Local builds do not take a Docker Hub namespace.'
  fi
}

load_image_selection() {
  # The caller supplies these after argument/engine/project resolution. Validate
  # the imported contract at call time without resetting any launcher state.
  : "${state_dir:?The launcher must resolve state_dir before loading images}" \
    "${rebuild:?The launcher must supply its rebuild selection}" \
    "${docker_cli:?The launcher must resolve its Docker executable}" \
    "${repo_dir:?The launcher must resolve its repository directory}"
  local file="$state_dir/images.env" key value source='' namespace='' tag='' layout='' seen='|'
  if [ -e "$file" ] || [ -L "$file" ]; then
    [ -f "$file" ] && [ ! -L "$file" ] || fail 'Saved image settings must be a regular file.'
    while IFS='=' read -r key value || [ -n "$key$value" ]; do
      case "$seen" in *"|$key|"*) fail 'Duplicate saved image setting.' ;; esac
      seen="$seen$key|"
      case "$key" in
        DS60_IMAGE_SOURCE) source="$value" ;;
        DS60_IMAGE_NAMESPACE) namespace="$value" ;;
        DS60_IMAGE_TAG) tag="$value" ;;
        DS60_IMAGE_LAYOUT) layout="$value" ;;
        *) fail 'Unexpected saved image setting; inspect this project images.env.' ;;
      esac
    done <"$file"
    [ -n "$source" ] && [ -n "$tag" ] && [[ "$seen" == *'|DS60_IMAGE_NAMESPACE|'* ]] || fail 'Saved image settings are incomplete.'
    if [ "$image_source_explicit" -eq 0 ]; then
      image_source="$source"
      image_namespace="$namespace"
    fi
    if [ "$image_layout_explicit" -eq 0 ]; then
      if [ "$image_source_explicit" -eq 0 ] && [ "$image_source" = hub ]; then
        # Three-field settings were written by the architecture-tag launcher.
        image_layout="${layout:-architecture}"
      else
        image_layout=manifest
      fi
    fi
    if [ "$image_tag_explicit" -eq 0 ]; then
      if [ "$image_source" = local ] && { [ "$rebuild" -eq 1 ] || [ "$image_source_explicit" -eq 1 ]; }; then
        image_tag="$release_version"
      else
        image_tag="$tag"
      fi
    fi
  fi
  validate_image_selection resolved
  if [ "$image_source" = hub ]; then
    image_arch="$("$docker_cli" info --format '{{.Architecture}}')"
    case "$image_arch" in x86_64 | amd64) image_arch=amd64 ;; aarch64 | arm64) image_arch=arm64 ;; *) fail 'Published classroom images support only Linux amd64 and arm64.' ;; esac
  fi
  export_image_selection
}

export_image_selection() {
  local profile _service local_name suffix variable _kind
  local source_root="${repo_dir:?The launcher must resolve its source directory}"
  while read -r profile _service local_name suffix variable _kind; do
    [[ "$profile" == \#* ]] && continue
    [ -n "$profile" ] || continue
    if [ "$image_source" = hub ]; then
      if [ "$image_layout" = architecture ]; then
        export "$variable=$image_namespace/ds60sqlpy:$image_tag-$suffix-$image_arch"
      elif [ "$profile" = app ]; then
        export "$variable=$image_namespace/ds60sqlpy:$image_tag"
      else
        export "$variable=$image_namespace/ds60sqlpy:$image_tag-$suffix"
      fi
    else
      export "$variable=$local_name:$image_tag"
    fi
  done <"$source_root/docker/classroom-images.tsv"
}

save_image_selection() {
  # Saving uses the same caller-owned project directory established by load.
  : "${state_dir:?The launcher must resolve state_dir before saving images}"
  local temporary
  temporary="$(mktemp "$state_dir/images.XXXXXX")"
  printf 'DS60_IMAGE_SOURCE=%s\nDS60_IMAGE_NAMESPACE=%s\nDS60_IMAGE_TAG=%s\n' "$image_source" "$image_namespace" "$image_tag" >"$temporary"
  if [ "$image_source" = hub ]; then
    printf 'DS60_IMAGE_LAYOUT=%s\n' "$image_layout" >>"$temporary"
  fi
  mv -f "$temporary" "$state_dir/images.env"
}

verify_hub_prepared_images() {
  [ "$image_source" = hub ] || return 0
  : "${docker_cli:?The launcher must resolve Docker before verifying images}" \
    "${image_arch:?The launcher must resolve the engine architecture}" \
    "${rebuild:?The launcher must supply its update selection}" \
    "${services[*]:?The launcher must supply selected worker services}"
  local service reference info image_os architecture identity extra
  for service in lab "${services[@]}"; do
    # Resume owns the existing container and its immutable image, even if its
    # original name was removed or now identifies a different prepared update.
    if [ "$rebuild" -eq 0 ] && [ -n "$(container_id "$service")" ]; then continue; fi
    reference="$(image_for "$service")"
    info="$("$docker_cli" image inspect --format '{{.Os}} {{.Architecture}} {{.Id}}' "$reference")" || fail "Could not inspect the prepared published image for $service. Saved volumes are retained."
    read -r image_os architecture identity extra <<<"$info"
    [ "$image_os" = linux ] && [ "$architecture" = "$image_arch" ] &&
      [[ "$identity" =~ ^sha256:[a-f0-9]{64}$ ]] && [ -z "${extra:-}" ] ||
      fail "The published image $reference does not match Linux/$image_arch. Correct the published platform tag before starting it. Saved volumes are retained."
    if [ "$service" = lab ] && [ -n "$resolved_latest_image_id" ]; then
      [ "$identity" = "$resolved_latest_image_id" ] || fail 'The cached versioned app differs from resolved latest. Use --rebuild to refresh published images while retaining saved volumes.'
    fi
  done
}

resolve_latest_hub_release() {
  [ "$image_source" = hub ] && [ "$image_tag" = latest ] || return 0
  [ "$image_layout" = manifest ] || fail 'latest requires the multi-platform image layout.'
  : "${no_build:?The launcher must supply its no-download selection}"
  local reference info image_os architecture identity extra resolved
  reference="$image_namespace/ds60sqlpy:latest"
  if [ "$no_build" -eq 1 ]; then
    "$docker_cli" image inspect "$reference" >/dev/null 2>&1 || fail 'latest is not cached locally. Plain resume retains the saved release; use ordinary startup to download a new release.'
  else
    # Retain a first installation's chosen source and small profile set before
    # the first network transfer. Existing installation preferences stay intact
    # if an attempted latest update cannot resolve a compatible release.
    if [ ! -e "$state_dir/images.env" ]; then
      save_profile_selection
      save_image_selection
    fi
    printf '\nResolving the published latest release...\n'
    "$docker_cli" image pull "$reference"
  fi
  info="$("$docker_cli" image inspect --format '{{.Os}} {{.Architecture}} {{.Id}}' "$reference")" || fail 'Could not inspect the latest image.'
  read -r image_os architecture identity extra <<<"$info"
  [ "$image_os" = linux ] && [ "$architecture" = "$image_arch" ] && [[ "$identity" =~ ^sha256:[a-f0-9]{64}$ ]] && [ -z "${extra:-}" ] || fail "The latest image does not match Linux/$image_arch. Saved volumes are retained."
  resolved="$("$docker_cli" image inspect --format '{{index .Config.Labels "org.opencontainers.image.version"}}' "$reference")" || fail 'Could not read the published release version.'
  [[ "$resolved" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || fail 'The latest image has no valid stable release-version label.'
  [ "$resolved" = "$release_version" ] || fail "The published release is $resolved, but this launcher is $release_version. Download the matching checkout or starter ZIP before installing it. Saved volumes are retained."
  image_tag="$resolved"
  resolved_latest_image_id="$identity"
  export_image_selection
  printf 'Resolved latest to %s. Future resumes retain this version.\n' "$image_tag"
}
