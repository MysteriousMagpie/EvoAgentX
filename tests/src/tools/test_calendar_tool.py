import unittest
from evoagentx.tools.calendar import CalendarTool

class TestCalendarTool(unittest.TestCase):
    def test_schemas(self):
        tool = CalendarTool()
        schemas = tool.get_tool_schemas()
        self.assertEqual(len(schemas), 4)
        names = [s["function"]["name"] for s in schemas]
        self.assertEqual(names, ["get_today", "add_event", "remove_event", "update_event"])

if __name__ == "__main__":
    unittest.main()
