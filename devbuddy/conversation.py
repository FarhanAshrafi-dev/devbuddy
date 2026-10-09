"""Interactive conversation and guarded action execution."""
from .action_registry import ExecutionContext
class ConversationManager:
 def __init__(self,router,registry,config,cli=None,input_fn=input,output_fn=print):self.router=router;self.registry=registry;self.config=config;self.cli=cli;self.input_fn=input_fn;self.output_fn=output_fn;self.cancelled=False
 def _handle_special_commands(self,cmd):
  cmd=cmd.strip().lower()
  if cmd in ("exit","quit"):self.cancelled=True;self.output_fn("Goodbye!");return True
  if cmd=="cancel":self.output_fn("Cancelled.");return True
  if cmd in ("help","menu"):
   self.output_fn("Commands: help, menu, status, cancel, exit\nAvailable actions:")
   for a in self.registry.list_all():self.output_fn(f"- {a.action_id}: {a.description}")
   return True
  if cmd=="status":self.output_fn("Ready. AI configured: "+str(bool(getattr(self.config,"openrouter_api_key",""))));return True
  return False
 def _present_plan(self,result):
  if not result.matched_actions:return False
  self.output_fn(result.explanation)
  for action_id in result.matched_actions:
   action=self.registry.get(action_id)
   if action:self.output_fn(f"Plan: {action.name} (risk: {action.risk_level.value})")
  return not result.clarification_questions and self.input_fn("Proceed? [y/N] ").strip().lower() in ("y","yes")
 def _execute_actions(self,actions,params):
  results=[];ctx=ExecutionContext(base_dir=__import__('pathlib').Path.cwd(),input_fn=self.input_fn,output_fn=self.output_fn)
  for action_id in actions:
   definition=self.registry.get(action_id)
   if not definition:continue
   values=params.get(action_id,{}) if isinstance(params,dict) else {}
   ok,errors,clean=self.registry.validate_params(action_id,values)
   if not ok: results.append(__import__('devbuddy.action_registry',fromlist=['ActionResult']).ActionResult(False,"Invalid parameters: "+"; ".join(errors)));continue
   try: results.append(definition.executor(clean,ctx))
   except Exception as exc:results.append(__import__('devbuddy.action_registry',fromlist=['ActionResult']).ActionResult(False,f"Action failed safely: {type(exc).__name__}: {exc}"))
  return results
 def handle_input(self,user_input):
  if self._handle_special_commands(user_input):return "Command handled."
  result=self.router.route(user_input)
  if result.clarification_questions:
   return "\n".join(result.clarification_questions)+"\n"+result.explanation
  if not result.matched_actions:return result.explanation
  if not self._present_plan(result):return "Plan cancelled."
  outcomes=self._execute_actions(result.matched_actions,result.parameters)
  return "\n".join(x.message for x in outcomes) or "No action executed."
 def start(self):
  self.output_fn("DevBuddy 🐍 — describe what you want to build. Type help for options.")
  while not self.cancelled:
   try:text=self.input_fn("\nYou: ")
   except (EOFError,KeyboardInterrupt):break
   self.output_fn(self.handle_input(text))
