        ---
        subject: Test Subject
        items:
          - Red
          - Green
          - Blue
        instructions: "List the items provided."
        ---
        # Prompt Instructions

        {{ instructions }}

        Items to list:
        {% for item in items %}
        - {{ item }}
        {% endfor %}

        The subject is: {{ subject }}
        ```
