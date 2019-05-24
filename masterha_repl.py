from checks import AgentCheck
from datadog_checks.utils.subprocess_output import get_subprocess_output



class CheckMHAReplicationStatus(AgentCheck):
    """This check provides metrics from a shell command
    WARNING: the user that dd-agent runs may need sudo access for the shell command
             sudo access is not required when running dd-agent as root (not recommended)
    """

    METRIC_NAME_PREFIX = "masterha_repl"

    def get_instance_config(self, instance):
        command = instance.get('command', None)
        metric_name = instance.get('metric_name', None)
        metric_type = instance.get('metric_type', 'gauge')
        tags = instance.get('tags', [])

        if command is None:
            raise Exception("A command must be specified in the instance")

        if metric_name is None:
            raise Exception("A metric_name must be specified in the instance")

        if metric_type != "gauge" and metric_type != "rate":
            message = "Unsupported metric_type: {0}".format(metric_type)
            raise Exception(message)

        metric_name = "{0}.{1}".format(self.METRIC_NAME_PREFIX, metric_name)

        config = {
            "command": command,
            "metric_name": metric_name,
            "metric_type": metric_type,
            "tags": tags
        }

        return config

    def check(self, instance):
        config = self.get_instance_config(instance)
        command = config.get("command")
        metric_name = config.get("metric_name")
        metric_type = config.get("metric_type")
        tags = config.get("tags")

        output, err, retcode = get_subprocess_output(command, self.log, raise_on_empty_output=True)

        if "MySQL Replication Health is OK." in output:
            self.gauge(metric_name, 1, tags=tags)
        else:
            self.gauge(metric_name, 0, tags=tags)