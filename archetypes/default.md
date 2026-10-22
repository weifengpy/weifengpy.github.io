---
title: "{{ replace .File.ContentBaseName "-" " " | title }}"
date: {{ .Date }}
slug: "{{ .File.ContentBaseName }}"
description: "" # REQUIRED, one or two sentences; this is the search-result snippet. CI fails if empty or duplicated.
tags: []
draft: true
---
