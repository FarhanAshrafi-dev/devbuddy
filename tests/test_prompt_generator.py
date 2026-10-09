from devbuddy.prompt_generator import PromptGenerator
def test_generate_returns_string():assert isinstance(PromptGenerator().generate("Task tracker"),str)
def test_generate_contains_objective():assert "## Objective" in PromptGenerator().generate("Task tracker")
def test_save_to_file(tmp_path):
 p=PromptGenerator().save_to_file("hello",tmp_path/"prompt.md");assert p.read_text()=="hello"
