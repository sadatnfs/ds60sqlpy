#!/usr/bin/env bash
# Sourced by the launcher. Values are data, never evaluated as shell code.
image_source=local
image_namespace=''
release_version=1.3.0
image_tag="$release_version"
image_source_explicit=0
image_tag_explicit=0
image_arch=''
image_layout=manifest
image_layout_explicit=0
image_tag_profiles=()
image_tag_versions=()
requested_image_tag_profiles=()
requested_image_tag_versions=()
resolved_latest_profiles=()
resolved_latest_ids=()
app_index_revision=''
app_index_source=''
image_selection_revision=''

valid_image_version() {
  [[ "$1" =~ ^[0-9]+\.[0-9]+\.[0-9]+([.-][a-zA-Z0-9][a-zA-Z0-9.-]*)?$ ]]
}

known_image_profile() {
  [ "$1" = app ] && return 0
  local profile _service _local_name _suffix _variable kind
  # classroom.sh resolves repo_dir before sourcing this helper.
  # shellcheck disable=SC2154
  while read -r profile _service _local_name _suffix _variable kind; do
    [ "$profile" != "$1" ] || {
      [ "$kind" = ordinary ]
      return
    }
  done <"$repo_dir/docker/classroom-images.tsv"
  return 1
}

request_image_tag() {
  local selection="$1" profile version known
  [[ "$selection" == *=* ]] || fail 'Use --image-tag PROFILE=VERSION, for example python-core=1.3.0.'
  profile="${selection%%=*}"
  version="${selection#*=}"
  known_image_profile "$profile" || fail "Unknown or unpublished image profile in --image-tag: $profile."
  [ "$version" = latest ] || [ "$version" = default ] || valid_image_version "$version" || fail 'Use --image-tag PROFILE=VERSION with a release version, latest or default.'
  for known in ${requested_image_tag_profiles[@]+"${requested_image_tag_profiles[@]}"}; do
    [ "$known" != "$profile" ] || fail "Choose one --image-tag value for $profile."
  done
  requested_image_tag_profiles+=("$profile")
  requested_image_tag_versions+=("$version")
}

image_tag_for() {
  local profile="$1" i
  for ((i = 0; i < ${#image_tag_profiles[@]}; i++)); do
    if [ "$profile" = "${image_tag_profiles[$i]}" ]; then
      printf '%s' "${image_tag_versions[$i]}"
      return
    fi
  done
  printf '%s' "$image_tag"
}

set_image_tag() {
  local profile="$1" version="$2" i
  for ((i = 0; i < ${#image_tag_profiles[@]}; i++)); do
    if [ "$profile" = "${image_tag_profiles[$i]}" ]; then
      image_tag_versions[$i]="$version"
      return
    fi
  done
  image_tag_profiles+=("$profile")
  image_tag_versions+=("$version")
}

clear_image_tag() {
  local requested="$1" i
  local -a remaining_profiles=() remaining_versions=()
  for ((i = 0; i < ${#image_tag_profiles[@]}; i++)); do
    [ "${image_tag_profiles[$i]}" != "$requested" ] || continue
    remaining_profiles+=("${image_tag_profiles[$i]}")
    remaining_versions+=("${image_tag_versions[$i]}")
  done
  image_tag_profiles=(${remaining_profiles[@]+"${remaining_profiles[@]}"})
  image_tag_versions=(${remaining_versions[@]+"${remaining_versions[@]}"})
}

validate_image_tag_compatibility() {
  local app_tag profile worker_tag app_line worker_line
  [ "$image_source" = hub ] || {
    [ "${#image_tag_profiles[@]}" -eq 0 ] || fail '--image-tag selects published Hub images; use --from-hub USER.'
    return 0
  }
  app_tag="$(image_tag_for app)"
  [ "$app_tag" = latest ] || valid_image_version "$app_tag" || fail 'The app image needs a release version or latest.'
  if [ "$app_tag" = latest ] || ! valid_image_version "$app_tag"; then return 0; fi
  app_line="${app_tag%.*}"
  # classroom.sh populates selected_profiles before calling this check.
  # shellcheck disable=SC2154
  for profile in "${selected_profiles[@]}"; do
    worker_tag="$(image_tag_for "$profile")"
    [ "$worker_tag" = latest ] && continue
    valid_image_version "$worker_tag" || fail "The $profile image needs a release version or latest."
    worker_line="${worker_tag%.*}"
    [ "$worker_line" = "$app_line" ] || fail "The $profile worker version $worker_tag is incompatible with app $app_tag. Choose a patch release in the same major.minor line. Saved volumes are retained."
  done
}

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
  local file="$state_dir/images.env" key value source='' namespace='' tag='' layout='' saved_revision='' seen='|' profile i reuse_saved_hub=0
  local -a saved_tag_profiles=() saved_tag_versions=()
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
        DS60_IMAGE_REVISION) saved_revision="$value" ;;
        DS60_IMAGE_TAG_*)
          profile="${key#DS60_IMAGE_TAG_}"
          known_image_profile "$profile" || fail "Unknown saved image profile: $profile."
          [ "$value" = latest ] || valid_image_version "$value" || fail "Invalid saved image version for $profile."
          saved_tag_profiles+=("$profile")
          saved_tag_versions+=("$value")
          ;;
        *) fail 'Unexpected saved image setting; inspect this project images.env.' ;;
      esac
    done <"$file"
    [ -n "$source" ] && [ -n "$tag" ] && [[ "$seen" == *'|DS60_IMAGE_NAMESPACE|'* ]] || fail 'Saved image settings are incomplete.'
    [ -z "$saved_revision" ] || [[ "$saved_revision" =~ ^[a-f0-9]{40}$ ]] || fail 'Invalid saved image revision.'
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
    if [ "$source" = hub ] && [ "$image_source" = hub ] && [ "$namespace" = "$image_namespace" ]; then
      reuse_saved_hub=1
    fi
    if [ "$image_tag_explicit" -eq 0 ]; then
      if [ "$image_source" = local ] && { [ "$rebuild" -eq 1 ] || [ "$image_source_explicit" -eq 1 ]; }; then
        image_tag="$release_version"
      elif [ "$image_source_explicit" -eq 1 ] && [ "$reuse_saved_hub" -eq 0 ]; then
        image_tag=latest
      else
        image_tag="$tag"
      fi
    fi
    if [ "$image_tag_explicit" -eq 0 ] && { [ "$image_source_explicit" -eq 0 ] || [ "$reuse_saved_hub" -eq 1 ]; }; then
      for ((i = 0; i < ${#saved_tag_profiles[@]}; i++)); do
        set_image_tag "${saved_tag_profiles[$i]}" "${saved_tag_versions[$i]}"
      done
      if [ "${#requested_image_tag_profiles[@]}" -eq 0 ]; then image_selection_revision="$saved_revision"; fi
    fi
  fi
  if [ "$image_source" = hub ] && [ "$image_source_explicit" -eq 1 ] && [ "$image_tag_explicit" -eq 0 ] && [ "$reuse_saved_hub" -eq 0 ]; then
    image_tag=latest
  fi
  for ((i = 0; i < ${#requested_image_tag_profiles[@]}; i++)); do
    if [ "${requested_image_tag_versions[$i]}" = default ]; then
      clear_image_tag "${requested_image_tag_profiles[$i]}"
    else
      set_image_tag "${requested_image_tag_profiles[$i]}" "${requested_image_tag_versions[$i]}"
    fi
  done
  image_tag="$(image_tag_for app)"
  validate_image_selection resolved
  [ "$image_source" = hub ] || [ "${#image_tag_profiles[@]}" -eq 0 ] || fail '--image-tag selects published Hub images; use --from-hub USER.'
  for ((i = 0; i < ${#image_tag_profiles[@]}; i++)); do
    if [ "${image_tag_versions[$i]}" = latest ]; then
      [ "$image_source" = hub ] && [ "$image_layout" = manifest ] || fail 'latest image tags require the multi-platform Hub layout.'
    fi
  done
  if [ "$image_source" = hub ]; then
    image_arch="$("$docker_cli" info --format '{{.Architecture}}')"
    case "$image_arch" in x86_64 | amd64) image_arch=amd64 ;; aarch64 | arm64) image_arch=arm64 ;; *) fail 'Published classroom images support only Linux amd64 and arm64.' ;; esac
  fi
  export_image_selection
}

export_image_selection() {
  local profile _service local_name suffix variable _kind profile_tag
  local source_root="${repo_dir:?The launcher must resolve its source directory}"
  while read -r profile _service local_name suffix variable _kind; do
    [[ "$profile" == \#* ]] && continue
    [ -n "$profile" ] || continue
    profile_tag="$(image_tag_for "$profile")"
    if [ "$image_source" = hub ]; then
      if [ "$image_layout" = architecture ]; then
        export "$variable=$image_namespace/ds60sqlpy:$profile_tag-$suffix-$image_arch"
      elif [ "$profile" = app ]; then
        export "$variable=$image_namespace/ds60sqlpy:$profile_tag"
      else
        export "$variable=$image_namespace/ds60sqlpy:$profile_tag-$suffix"
      fi
    else
      export "$variable=$local_name:$profile_tag"
    fi
  done <"$source_root/docker/classroom-images.tsv"
}

save_image_selection() {
  # Saving uses the same caller-owned project directory established by load.
  : "${state_dir:?The launcher must resolve state_dir before saving images}"
  local temporary i
  temporary="$(mktemp "$state_dir/images.XXXXXX")"
  printf 'DS60_IMAGE_SOURCE=%s\nDS60_IMAGE_NAMESPACE=%s\nDS60_IMAGE_TAG=%s\n' "$image_source" "$image_namespace" "$image_tag" >"$temporary"
  if [ "$image_source" = hub ]; then
    printf 'DS60_IMAGE_LAYOUT=%s\n' "$image_layout" >>"$temporary"
    [ -z "$image_selection_revision" ] || printf 'DS60_IMAGE_REVISION=%s\n' "$image_selection_revision" >>"$temporary"
    for ((i = 0; i < ${#image_tag_profiles[@]}; i++)); do
      [ "${image_tag_profiles[$i]}" != app ] || continue
      printf 'DS60_IMAGE_TAG_%s=%s\n' "${image_tag_profiles[$i]}" "${image_tag_versions[$i]}" >>"$temporary"
    done
  fi
  mv -f "$temporary" "$state_dir/images.env"
}

verify_hub_prepared_images() {
  [ "$image_source" = hub ] || return 0
  : "${docker_cli:?The launcher must resolve Docker before verifying images}" \
    "${image_arch:?The launcher must resolve the engine architecture}" \
    "${rebuild:?The launcher must supply its update selection}" \
    "${services[*]:?The launcher must supply selected worker services}"
  local service reference info image_os architecture identity extra profile i
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
    profile="$(image_profile_for_service "$service")"
    for ((i = 0; i < ${#resolved_latest_profiles[@]}; i++)); do
      if [ "$profile" = "${resolved_latest_profiles[$i]}" ]; then
        [ "$identity" = "${resolved_latest_ids[$i]}" ] || fail "The versioned $profile image differs from its resolved latest alias. Saved volumes are retained."
      fi
    done
  done
}

image_profile_for_service() {
  local profile service _local_name _suffix _variable _kind
  while read -r profile service _local_name _suffix _variable _kind; do
    [ "$service" != "$1" ] || {
      printf '%s' "$profile"
      return 0
    }
  done <"$repo_dir/docker/classroom-images.tsv"
  fail "Unknown image service: $1."
}

latest_alias_for_profile() {
  local requested="$1" profile _service _local_name suffix _variable _kind
  while read -r profile _service _local_name suffix _variable _kind; do
    [ "$profile" != "$requested" ] || {
      if [ "$profile" = app ]; then
        printf '%s/ds60sqlpy:latest' "$image_namespace"
      else printf '%s/ds60sqlpy:latest-%s' "$image_namespace" "$suffix"; fi
      return 0
    }
  done <"$repo_dir/docker/classroom-images.tsv"
  fail "Unknown image profile: $requested."
}

read_published_index_metadata() {
  local reference="$1" expected_profile="$2" record media schema profile version revision source platforms extra
  "$docker_cli" buildx version >/dev/null 2>&1 || fail "Docker Buildx is required to validate $expected_profile latest or a mixed worker version. Install/enable Buildx, or choose a concrete matching release. Saved volumes are retained."
  record="$("$docker_cli" buildx imagetools inspect --format '{{.Manifest.MediaType}}|{{index .Manifest.Annotations "io.ds60.release.schema"}}|{{index .Manifest.Annotations "io.ds60.release.profile"}}|{{index .Manifest.Annotations "org.opencontainers.image.version"}}|{{index .Manifest.Annotations "org.opencontainers.image.revision"}}|{{index .Manifest.Annotations "org.opencontainers.image.source"}}|{{range .Manifest.Manifests}}{{.Platform.OS}}/{{.Platform.Architecture}};{{end}}' "$reference" 2>/dev/null)" || fail "Could not inspect published index metadata for $expected_profile at $reference. Choose a concrete matching release if Buildx or registry metadata is unavailable. Saved volumes are retained."
  [ "${#record}" -le 2048 ] && [[ "$record" != *$'\n'* ]] || fail "Unexpected index metadata for $expected_profile. Saved volumes are retained."
  IFS='|' read -r media schema profile version revision source platforms extra <<<"$record"
  [ "$media" = application/vnd.oci.image.index.v1+json ] && [ "$schema" = 1 ] && [ "$profile" = "$expected_profile" ] &&
    [[ "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] && [[ "$revision" =~ ^[a-f0-9]{40}$ ]] &&
    [[ "$source" =~ ^https://github[.]com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$ ]] &&
    [[ "$platforms" =~ ^(linux/amd64\;linux/arm64\;|linux/arm64\;linux/amd64\;)$ ]] && [ -z "${extra:-}" ] ||
    fail "The published index for $expected_profile lacks trusted release/profile/revision/source or both native platforms. Choose a concrete matching release. Saved volumes are retained."
  inspected_index_version="$version"
  inspected_index_revision="$revision"
  inspected_index_source="$source"
}

ensure_app_index_metadata() {
  [ -z "$app_index_revision" ] || return 0
  read_published_index_metadata "$image_namespace/ds60sqlpy:$image_tag" app
  [ "$inspected_index_version" = "$image_tag" ] || fail "The app index version does not match selected app $image_tag. Saved volumes are retained."
  app_index_revision="$inspected_index_revision"
  app_index_source="$inspected_index_source"
}

verify_mixed_worker_release_metadata() {
  local profile worker_tag suffix reference _service _local_name _variable _kind catalog_profile cached_revision="$image_selection_revision"
  for profile in "${selected_profiles[@]}"; do
    worker_tag="$(image_tag_for "$profile")"
    [ "$worker_tag" != "$image_tag" ] || continue
    [ "$image_layout" = manifest ] || fail "Mixed image versions require combined Hub indexes; $profile uses $worker_tag. Saved volumes are retained."
    # classroom.sh sets no_build before calling release verification.
    # shellcheck disable=SC2154
    if [ "$no_build" -eq 1 ]; then
      [ -n "$image_selection_revision" ] || fail "The mixed $profile image selection has not been verified. Resume cannot query the registry; run ordinary ./classroom to validate it. Saved volumes are retained."
      continue
    fi
    if [ "$rebuild" -eq 0 ] && [ -n "$cached_revision" ]; then continue; fi
    ensure_app_index_metadata
    suffix=''
    while read -r catalog_profile _service _local_name _suffix _variable _kind; do
      if [ "$catalog_profile" = "$profile" ]; then
        suffix="$_suffix"
        break
      fi
    done <"$repo_dir/docker/classroom-images.tsv"
    [ -n "$suffix" ] || fail "Unknown image profile: $profile."
    reference="$image_namespace/ds60sqlpy:$worker_tag-$suffix"
    read_published_index_metadata "$reference" "$profile"
    [ "$inspected_index_version" = "$worker_tag" ] && [ "$inspected_index_revision" = "$app_index_revision" ] && [ "$inspected_index_source" = "$app_index_source" ] ||
      fail "The $profile worker version $worker_tag is not qualified with app $image_tag from the same source revision. Choose a matching published release; saved volumes are retained."
    image_selection_revision="$app_index_revision"
  done
}

resolve_latest_hub_release() {
  [ "$image_source" = hub ] || return 0
  : "${no_build:?The launcher must supply its no-download selection}"
  local profile reference info image_os architecture identity extra resolved worker_revision worker_source
  for profile in app "${selected_profiles[@]}"; do
    [ "$(image_tag_for "$profile")" = latest ] || continue
    [ "$image_layout" = manifest ] || fail 'latest requires the multi-platform image layout.'
    if [ "$no_build" -eq 1 ]; then
      fail "Cannot resolve $profile=latest during resume/--no-build. Resume never pulls or follows latest; use ordinary ./classroom to finish preparation. Saved volumes are retained."
    fi
    # An interrupted first selection remains retryable. Existing saved choices
    # are not replaced if the registry alias or its version metadata is invalid.
    if [ ! -e "$state_dir/images.env" ]; then
      save_profile_selection
      save_image_selection
    fi
    reference="$(latest_alias_for_profile "$profile")"
    printf '\nResolving published latest for %s...\n' "$profile"
    if [ "$profile" != app ]; then
      read_published_index_metadata "$reference" "$profile"
      resolved="$inspected_index_version"
      worker_revision="$inspected_index_revision"
      worker_source="$inspected_index_source"
      ensure_app_index_metadata
      [ "$worker_revision" = "$app_index_revision" ] && [ "$worker_source" = "$app_index_source" ] ||
        fail "The latest $profile worker is not qualified with app $image_tag from the same source revision. Choose a matching version; saved volumes are retained."
    fi
    "$docker_cli" image pull "$reference" || fail "Could not pull the latest alias for $profile. Check that this profile was published; saved volumes are retained."
    info="$("$docker_cli" image inspect --format '{{.Os}} {{.Architecture}} {{.Id}}' "$reference")" || fail "Could not inspect the latest $profile image."
    read -r image_os architecture identity extra <<<"$info"
    [ "$image_os" = linux ] && [ "$architecture" = "$image_arch" ] && [[ "$identity" =~ ^sha256:[a-f0-9]{64}$ ]] && [ -z "${extra:-}" ] || fail "The latest $profile image does not match Linux/$image_arch. Saved volumes are retained."
    if [ "$profile" = app ]; then
      resolved="$("$docker_cli" image inspect --format '{{index .Config.Labels "org.opencontainers.image.version"}}' "$reference")" || fail 'Could not read the published app release version.'
      [[ "$resolved" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || fail 'The latest app image has no valid stable release-version label. Saved volumes are retained.'
    fi
    if [ "$profile" = app ]; then
      [ "$resolved" = "$release_version" ] || fail "The published release is $resolved, but this launcher is $release_version. Download the matching checkout or starter ZIP before installing it. Saved volumes are retained."
      image_tag="$resolved"
    fi
    set_image_tag "$profile" "$resolved"
    resolved_latest_profiles+=("$profile")
    resolved_latest_ids+=("$identity")
    printf 'Resolved %s latest to %s. Future resumes retain this version.\n' "$profile" "$resolved"
  done
  validate_image_tag_compatibility
  verify_mixed_worker_release_metadata
  export_image_selection
}
