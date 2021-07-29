#!/bin/bash -e
image_name=pedrohgv/convert-pascal-2-yolo-op
image_tag=latest
full_image_name=${image_name}:${image_tag}

docker build -t "${full_image_name}" .
docker push "$full_image_name"

# Output the strict image name, which contains the sha256 image digest
docker inspect --format="{{index .RepoDigests 0}}" "${full_image_name}"