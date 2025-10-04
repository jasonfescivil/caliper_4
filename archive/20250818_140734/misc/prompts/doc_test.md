---
template_goal: "Summarize the source document."
other_data: 123
---
# Task
{{ template_goal }}

## Source Document Content (`sample.txt`)

text
{{ source_docs['sample.txt'] }}

Other data from front matter: {{ other_data }}
---