from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, before_kickoff, after_kickoff

# Uncomment the following line to use an example of a custom tool
# from sex_educator.tools.custom_tool import MyCustomTool

# Check our tools documentations for more information on how to use them
# from crewai_tools import SerperDevTool
from tools.SerperDevTool import SerperDevTool

@CrewBase
class SexEducator():
	"""SexEducator crew"""

	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	@before_kickoff # Optional hook to be executed before the crew starts
	def pull_data_example(self, inputs):
		# Example of pulling data from an external API, dynamically changing the inputs
		inputs['extra_data'] = "This is extra data"
		return inputs

	@after_kickoff # Optional hook to be executed after the crew has finished
	def log_results(self, output):
		# Example of logging results, dynamically changing the output
		print(f"Results: {output}")
		return output

	# @agent
	# def researcher(self) -> Agent:
	# 	return Agent(
	# 		config=self.agents_config['researcher'],
	# 		# tools=[MyCustomTool()], # Example of custom tool, loaded on the beginning of file
	# 		verbose=True
	# 	)

	# @agent
	# def reporting_analyst(self) -> Agent:
	# 	return Agent(
	# 		config=self.agents_config['reporting_analyst'],
	# 		verbose=True
	# 	)

	# @task
	# def research_task(self) -> Task:
	# 	return Task(
	# 		config=self.tasks_config['research_task'],
	# 	)

	# @task
	# def reporting_task(self) -> Task:
	# 	return Task(
	# 		config=self.tasks_config['reporting_task'],
	# 		output_file='report.md'
	# 	)
	# --- AGENT METHODS ---
	@agent
	def researcher(self) -> Agent:
		return Agent(
			config=self.agents_config['researcher'],
			tools=[SerperDevTool()],
			verbose=True
		)

	@agent
	def reporting_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['reporting_analyst'],
			verbose=True
		)

	@agent
	def curriculum_curator(self) -> Agent:
		return Agent(
			config=self.agents_config['curriculum_curator'],
			tools=[SerperDevTool()],
			verbose=True
		)

	@agent
	def conversation_handler(self) -> Agent:
		return Agent(
			config=self.agents_config['conversation_handler'],
			verbose=True
		)

	@agent
	def cultural_adapter(self) -> Agent:
		return Agent(
			config=self.agents_config['cultural_adapter'],
			verbose=True
		)

	@agent
	def legal_compliance(self) -> Agent:
		return Agent(
			config=self.agents_config['legal_compliance'],
			verbose=True
		)

	@agent
	def outreach_engagement(self) -> Agent:
		return Agent(
			config=self.agents_config['outreach_engagement'],
			verbose=True
		)

	@agent
	def escalation_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['escalation_agent'],
			verbose=True
		)

	@agent
	def feedback_analyzer(self) -> Agent:
		return Agent(
			config=self.agents_config['feedback_analyzer'],
			verbose=True
		)

	# --- TASK METHODS ---
	@task
	def research_task(self) -> Task:
		return Task(
			config=self.tasks_config['research_task'],
		)

	@task
	def reporting_task(self) -> Task:
		return Task(
			config=self.tasks_config['reporting_task'],
		)

	@task
	def curriculum_curation_task(self) -> Task:
		return Task(
			config=self.tasks_config['curriculum_curation_task'],
		)

	@task
	def localization_task(self) -> Task:
		return Task(
			config=self.tasks_config['localization_task'],
		)

	@task
	def legal_review_task(self) -> Task:
		return Task(
			config=self.tasks_config['legal_review_task'],
		)

	@task
	def user_query_handling_task(self) -> Task:
		return Task(
			config=self.tasks_config['user_query_handling_task'],
		)

	@task
	def escalation_handling_task(self) -> Task:
		return Task(
			config=self.tasks_config['escalation_handling_task'],
		)

	@task
	def outreach_and_accessibility_task(self) -> Task:
		return Task(
			config=self.tasks_config['outreach_and_accessibility_task'],
		)

	@task
	def feedback_analysis_task(self) -> Task:
		return Task(
			config=self.tasks_config['feedback_analysis_task'],
		)


	@crew
	def crew(self) -> Crew:
		"""Creates the SexEducator crew"""
		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)
