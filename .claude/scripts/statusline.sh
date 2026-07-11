#!/bin/bash
project=$(basename "$PWD")
branch=$(git branch --show-current 2>/dev/null)
if [ -n "$branch" ]; then
  echo "📁 $project  │  🌿 $branch"
else
  echo "📁 $project"
fi
