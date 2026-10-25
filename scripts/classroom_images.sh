#!/usr/bin/env bash
# Sourced by the launcher. Values are data, never evaluated as shell code.
image_source=local
image_namespace=''
release_version=0.4.0
image_tag="$release_version"
image_source_explicit=0
image_tag_explicit=0
image_arch=''

validate_image_selection() {
  case "$image_source" in local | hub) ;; *) fail 'Image source must be local or hub.' ;; esac
  [[ "$image_tag" =~ ^[0-9]+\.[0-9]+\.[0-9]+([.-][a-zA-Z0-9][a-zA-Z0-9.-]*)?$ ]] || fail 'Use a release tag such as 0.4.0, not latest or a shell expression.'
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
  local file="$state_dir/images.env" key value source='' namespace='' tag='' seen='|'
  if [ -e "$file" ] || [ -L "$file" ]; then
    [ -f "$file" ] && [ ! -L "$file" ] || fail 'Saved image settings must be a regular file.'
    while IFS='=' read -r key value || [ -n "$key$value" ]; do
      case "$seen" in *"|$key|"*) fail 'Duplicate saved image setting.' ;; esac
      seen="$seen$key|"
      case "$key" in
        DS60_IMAGE_SOURCE) source="$value" ;;
        DS60_IMAGE_NAMESPACE) namespace="$value" ;;
        DS60_IMAGE_TAG) tag="$value" ;;
        *) fail 'Unexpected saved image setting; inspect this project images.env.' ;;
      esac
    done <"$file"
    [ -n "$source" ] && [ -n "$tag" ] && [[ "$seen" == *'|DS60_IMAGE_NAMESPACE|'* ]] || fail 'Saved image settings are incomplete.'
    if [ "$image_source_explicit" -eq 0 ]; then
      image_source="$source"
      image_namespace="$namespace"
    fi
    if [ "$image_tag_explicit" -eq 0 ]; then
      if [ "$image_source" = local ] && { [ "$rebuild" -eq 1 ] || [ "$image_source_explicit" -eq 1 ]; }; then
        image_tag="$release_version"
      else
        image_tag="$tag"
      fi
    fi
  fi
  validate_image_selection
  if [ "$image_source" = hub ]; then
    image_arch="$("$docker_cli" info --format '{{.Architecture}}')"
    case "$image_arch" in x86_64 | amd64) image_arch=amd64 ;; aarch64 | arm64) image_arch=arm64 ;; *) fail 'Published classroom images support only Linux amd64 and arm64.' ;; esac
  fi
  local profile _service local_name suffix variable _kind
  while read -r profile _service local_name suffix variable _kind; do
    [[ "$profile" == \#* ]] && continue
    [ -n "$profile" ] || continue
    if [ "$image_source" = hub ]; then
      export "$variable=$image_namespace/ds60sqlpy:$image_tag-$suffix-$image_arch"
    else
      export "$variable=$local_name:$image_tag"
    fi
  done <"$repo_dir/docker/classroom-images.tsv"
}

save_image_selection() {
  # Saving uses the same caller-owned project directory established by load.
  : "${state_dir:?The launcher must resolve state_dir before saving images}"
  local temporary
  temporary="$(mktemp "$state_dir/images.XXXXXX")"
  printf 'DS60_IMAGE_SOURCE=%s\nDS60_IMAGE_NAMESPACE=%s\nDS60_IMAGE_TAG=%s\n' "$image_source" "$image_namespace" "$image_tag" >"$temporary"
  mv -f "$temporary" "$state_dir/images.env"
}
