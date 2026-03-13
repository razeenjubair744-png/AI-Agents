from crewai import Agent, Task, Crew
import os
os.environ["CREWAI_TESTING"] = "true"
from utils import get_openai_api_key

# set the OpenAI model (gpt-4o-mini)
os.environ["MODEL"] = "gpt-4o-mini"
# set up the OpenAI API key 
os.environ["OPENAI_API_KEY"] = get_openai_api_key()


# import the tools
from crewai_tools import EXASearchTool, ScrapeWebsiteTool
from utils import get_exa_api_key

# set the exa API key
os.environ["EXA_API_KEY"] = get_exa_api_key()



# Create the EXASearchTool instance
exa_search_tool = EXASearchTool(base_url=os.getenv("EXA_BASE_URL"))
# Create the ScrapeWebsiteTool instance
scrape_website_tool = ScrapeWebsiteTool()

# Define the Research Planner Agent
research_planner = Agent(
    role="Research Planner",
    goal="Analyze queries and break them down into smaller, specific research topics.",
    backstory=(
         "You are a research strategist who excels at breaking down complex questions "
         "into manageable research components. You identify what needs to be researched "
         "and create clear research objectives."
    ),
    verbose=True, # set to True to see detailed agent actions
    max_rpm=150,
    max_iter=15
)

# Researcher Agent
researcher = Agent(
    role="Internet Researcher",
    goal="Research thoroughly all assigned topics",
    ### START CODE HERE ###
    backstory=(
        "You are a world-class researcher , who is experienced in researching all the topics"
        "whatever topics , what you are given!!"
    ),
    # add the 2 tool instances you created
    tools=[exa_search_tool, scrape_website_tool],
    ### END CODE HERE ###
    verbose=True,
    max_rpm=150,
    max_iter=15
)

# Fact Checker Agent
fact_checker = Agent(
    role="Fact Checker",
    goal=(
        "Verify data for accuracy, identify inconsistencies, "
        "and flag potential misinformation"
    ),
    
    backstory=( 
        "You are an excellent evaluator, and debugger and your work is to verify data"
        "for accuracy and flag potential errors"
    ),
    tools=[exa_search_tool, scrape_website_tool],

    verbose=True,
    max_rpm=150,
    max_iter=15
)

# Report Writer Agent
report_writer = Agent(
    role="Report Writer",
    goal="Write clear, concise, and well-structured reports based on gathered information",
    
    backstory=( 
         "You are an excellent report writer. Think yourself as William Shakespeare , And you are "
         "able to write report on a structured way."
    ),
   
    verbose=True,max_rpm=150,
    max_iter=15
)
  
# Let's create the tasks

# define the create research plan task
create_research_plan_task = Task(
    description=(
        "Based on the user's query, break it down into specific topics and key questions, "
        "and create a focused research plan."
        "The user's query is: {user_query}"
    ),
    expected_output=(
        "A research plan with main research topics to investigate, "
        "key questions for each topic, and success criteria for the research."
        ),
    agent=research_planner,
)

# define the gather research data task
gather_research_data_task = Task(
    description=(
        "Using the research plan, collect information on all identified topics. "
        "Cite all sources used."
    ),
   
    expected_output=(
        "Citation of all the sources needed for this task"
    ),
    agent=researcher
    
)

#define the verify information quality task
verify_information_quality_task = Task(
    description=(
        "Review all collected research. Identify any conflicting information, "
        "potential misinformation, or gaps that need addressing."
    ),
   
    expected_output=( 
        "List of all the conflicting and potential misinformation , that needs addressing"
    ),
    agent=fact_checker
   
)

# define the write final report task
write_final_report_task = Task(
    description=(
        "Create a comprehensive report that answers the original query using all verified research data. "
        "Structure it with clear sections, include citations, and provide actionable insights."
    ),
    
    expected_output=( 
        "A beautiful Markdown report that showcases the important point only , and also you can use emoji"
        "within if you want "
    ),
    agent=report_writer
    
)

# create the crew with the defined agents and tasks
crew = Crew(
    
    agents=[research_planner, researcher, fact_checker, report_writer],
    tasks=[create_research_plan_task, gather_research_data_task, verify_information_quality_task, write_final_report_task]
   
)

user_query = "Conduct a deep research about the recent news on the killing of Osman Hadi in Bangladesh\n"
"If you fail then you can conduct a deep research on the current activities of unfpa in bangladesh?"

result = crew.kickoff(inputs = {
    "user_query": user_query
})
    

 





