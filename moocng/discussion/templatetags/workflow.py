from django import template

from moocng.discussion import workflow

register = template.Library()

class WorkflowNode(template.Node):

    def __init__(self, func_name, args, var_name=None):
        self.args = args
        self.var_name = var_name
        self.func_name = func_name.split("workflow.")[1]

    def render(self, context):
        func = getattr(workflow, self.func_name)
        args = []
        for arg in self.args:
            args.append(template.Variable(arg).resolve(context))
        result = func(*args)
        if self.var_name:
            context[self.var_name] = result
            return ''
        else:
            return result

def workflow_func(parser, token):
    # This version uses a regular expression to parse tag contents.
    try:
        # Splitting by None == splitting by spaces.
        tag_name, args = token.contents.split(None, 1)
    except ValueError:
        msg = "%r tag requires arguments" % token.contents.split()[0]
        raise template.TemplateSyntaxError(msg)
    args = token.split_contents()[1:]
    if "as" in args and args.index("as") == len(args) - 2:
        var_name = args[-1]
        args = args[:-2]
    else:
        var_name = None
    return WorkflowNode(tag_name, args, var_name)

for f in dir(workflow):
    if f.startswith("can_"):
        register.tag("workflow.%s" % f, workflow_func)
