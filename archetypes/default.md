---
title: "{{ replace .File.ContentBaseName "-" " " | title }}"
date: {{ .Date }}
slug: "{{ .File.ContentBaseName }}"
description: "" # REQUIRED, one or two sentences; this is the search-result snippet. CI fails if empty or duplicated.
image: "" # OPTIONAL, filename of a page-bundle image (e.g. a diagram SVG) shown as a thumbnail at the left of this post's entry on /posts/. Leave empty for no thumbnail.
draft: true
---
