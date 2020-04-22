from rasa_core.channels import HttpInputChannel
from rasa_core.agent import Agent
from rasa_core.interpreter import RasaNLUInterpreter
from rasa_slack_connector import SlackInput


nlu_interpreter = RasaNLUInterpreter('./models/nlu/default/restaurantnlu')
agent = Agent.load('./models/dialogue', interpreter = nlu_interpreter)

input_channel = SlackInput('xoxp-789352985890-804344370262-803993977159-a1669ffb998fcb9b94b0e91d688bb971', #app verification token
							'xoxb-789352985890-802145143285-gpcpJezvqlHjYMTzV0DcXjTi', # bot verification token
							'hWddhaR6N4ZkzqntS7tgInir', # slack verification token
							True)

agent.handle_channel(HttpInputChannel(5004, '/', input_channel))