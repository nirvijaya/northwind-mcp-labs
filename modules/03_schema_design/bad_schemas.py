"""Three intentionally bad Claude API tool definitions. Find every problem.

Don't fix this file; write the good versions in starter.py.
"""

BAD_TOOLS = [
    {
        "name": "doStuff",
        "description": "gets tickets",
        "input_schema": {
            "type": "object",
            "properties": {
                "q": {"type": "string"},
            },
        },
    },
    {
        "name": "ticket",
        "description": "ticket",
        "input_schema": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
            },
        },
    },
    {
        "name": "Find_Tickets_By_Filter_v2",
        "description": "Filter.",
        "input_schema": {
            "type": "object",
            "properties": {
                "status": {"type": "string", "description": "status"},
                "priority": {"type": "string"},
                "dept": {"type": "string"},
                "max": {"type": "number"},
            },
            "required": ["status", "priority", "dept", "max"],
        },
    },
]
