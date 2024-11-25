import streamlit as st
import google.generativeai as genai
import io
from google.cloud import bigquery

##___________________________________________ GenAI setup ________________________________________##

genai.configure(api_key='AIzaSyBAsGoEgU4TsyPRcbbchUy_LYY7NzITM0E')

model = genai.GenerativeModel('gemini-pro')


##____________________________________________ Set the page configuration_________________________##
st.set_page_config(
  page_title="Meal Planner",
  page_icon="☕",
  layout="wide",
)

##_______________________________________________ background _____________________________________##
st.markdown("<p class='title'>Meal Planner</p>", unsafe_allow_html=True)

st.markdown(
  """
  <style>
    .title {
      font-family: 'Jomhuria', sans-serif;
      font-size: 48px;
      font-weight: bold;
      color: white;
      text-align: center;
      padding: 0px;
    }
  </style>
  """,
  unsafe_allow_html=True,
)
col1, col2, col3 = st.columns([1,1.3,1])

with col1:
  st.write("")

with col2:
  st.image("fitness-webapp\\Nowshin-Meal-Planner\\giphy.gif", width= 200)

with col3:
  st.write("")


##_______________________________________________ sidebar ________________________________________##
sidebar = st.sidebar

#------------------------------------------------- User BigQuery ---------------------------------##
# Initialize a BigQuery client
client = bigquery.Client(project='nowshintechx')

# Define the table where you want to store the data
table_id = "nowshintechx.meal_planner.user_info"


#-------------------------------------------------Add User ------------------------------------------##
# Fetching names
query = f"SELECT name FROM `{table_id}`"
query_job = client.query(query)
names = [row.name for row in query_job]

with sidebar.popover("Add new user"):
  st.markdown("Hi! Add yourself 👋")
  name = st.text_input('Name', placeholder='Your name', help='Your name')
  sex = st.selectbox('Sex', ['Male', 'Female'], index=None, placeholder="Choose an option")
  age = st.number_input('Age', 0)
  height = st.text_input('Height (cm)', placeholder='cm pls', help='You can\'t convert? Are you dumb?')
  weight = st.text_input('Weight (Kg)', placeholder='kg pls', help='You can\'t convert? Are you dumb?')

  if st.button('Save'):
    if name not in names:
      # Store the inputs in session_state
      st.session_state.user_data = {
        'name': name,
        'sex': sex,
        'age': age,
        'height': height,
        'weight': weight
      }

      # Prepare the data to be inserted into BigQuery
      rows_to_insert = [
        {"name": name, "sex": sex, "age": age, "height": height, "weight": weight},
      ]

      # Insert the data into the BigQuery table
      errors = client.insert_rows_json(table_id, rows_to_insert)
      if errors == []:
        st.success('User data saved!')
      else:
        st.error('Failed to save user data!')
    else:
      st.error('This user already exits')


#--------------------------------------------select User -----------------------------------------##  

# Fetching usernames
query = f"SELECT name FROM `{table_id}`"
query_job = client.query(query)
user_names =  [row.name for row in query_job]

user = sidebar.selectbox(
  'Select User',
  user_names,
  index=None,
  placeholder="Choose an option",
)

if user:
  # Fetch the selected user's information from the BigQuery table
  query = f"SELECT * FROM `{table_id}` WHERE name = '{user}'"
  query_job = client.query(query)
  user_info = [dict(row) for row in query_job][0]

  # Store the user's information in variables
  name = user_info['Name']
  sex = user_info['Sex']
  age = user_info['Age']
  height = user_info['Height']
  weight = user_info['Weight']

with st.expander("User Info"):
  st.write("User name: " + name)
  st.write("Sex: " + str(sex))
  st.write("Age: " + str(age))
  st.write("Height: " + str(height))
  st.write("Weight: " + str(weight))

# --------------------------------------Adding Ingredients----------------------------------------##

# Check if 'ingredients' is in session_state
if "ingredients" not in st.session_state:
  st.session_state.ingredients = []

# Get new ingredient from user
new_ingredient = st.sidebar.text_input(
  label='Tell us what ingredients you need to use up',
  placeholder='Type here',
  help='Type it out, separate by comma',
)

previous_ingredient_list = ['Onion', 'Chicken', 'Potato', 'Rice', 'Milk', 'Garlic']

# Check if 'total_list', 'selected_ingredients' and 'final_ingredient_list' are in session_state

if "total_list" not in st.session_state:
  st.session_state.total_list = previous_ingredient_list
if "selected_ingredients" not in st.session_state:
  st.session_state.selected_ingredients = [False]*len(st.session_state.total_list)
if "final_ingredient_list" not in st.session_state:
  st.session_state.final_ingredient_list = st.session_state.total_list.copy()

# If user has entered a new ingredient, add it to the list
if st.sidebar.button('Add Ingredient'):
  if new_ingredient not in previous_ingredient_list:
    if new_ingredient != "":
    # Split the input by comma and strip whitespace
      new_ingredients = [ing.strip() for ing in new_ingredient.split(',')]
      st.session_state.ingredients.extend(new_ingredients)
      st.session_state.total_list.extend(new_ingredients)  # Add new ingredients to total_list
      st.session_state.selected_ingredients.extend([False]*len(new_ingredients))  # Add False for each new ingredient
      st.session_state.final_ingredient_list = st.session_state.total_list.copy()  # Update final_ingredient_list
  else:
    sidebar.error("This item already exists in the list.")

sidebar.markdown("Your ingredients so far:")
# Create a checkbox for each ingredient in total_list
for i, ingredient in enumerate(st.session_state.total_list):
  if st.sidebar.checkbox(ingredient, value=st.session_state.selected_ingredients[i]):
    st.session_state.selected_ingredients[i] = True
  else:
    st.session_state.selected_ingredients[i] = False

# If the 'Remove' button is clicked, remove the selected ingredients
if st.sidebar.button('Remove'):
  # Iterate in reverse to avoid changing indices during removal
  for i in range(len(st.session_state.total_list)-1, -1, -1):
    if st.session_state.selected_ingredients[i]:
      del st.session_state.total_list[i]
      del st.session_state.selected_ingredients[i]
  st.session_state.final_ingredient_list = st.session_state.total_list.copy()  # Update final_ingredient_list after removal
  # Force Streamlit to rerun the app
  st.experimental_rerun()

# st.sidebar.markdown(st.session_state.final_ingredient_list)


#-------------------------------------- culinary preference --------------------------------------##
culinary_pref = sidebar.selectbox(
  'Culinary Preference',
  ['Indian', 'mediterranean', 'Italian','Thai', 'Chinese', 'Bangladeshi', 'Mexican', 'Japanese', 'Korean', 'French'],
  help='Indecisive? Go see therapist!',
  index=None,
  placeholder="Choose an option",
)

#-------------------------------------------- dietary restreiction -------------------------------##
dietary_res = sidebar.multiselect(
  'Dietary Restrictions',
  ['Halal','Kosher','Vegetarian','Vegan','Pescatarian'],
  help='If you don\'t know what dietary restriction is, then you don\'t have any dietary restriction LOL.'
)

#--------------------------------------------- Allergies -----------------------------------------##
allergies = sidebar.text_input(
  'Allergies',
  placeholder='if none, keep empty',
  help='No allergy? Darwin is proud of you. Keep this box empty'
)

#----------------------------------------------- Health Goal -------------------------------------##
health_goal = sidebar.multiselect(
  'Health Goals',
  ['Wanna lose weight', 'Wanna gain muscle', 'Wanna regulate hormone', 'Wanna gain weight', 'Want nuitrition to recover', 'Feeling festive', 'What\'s the point? Will die anyways.'],
  help='No matter what you do, you WILL DIE'
)

# # Calorie range 
# # calorie range is a tuple here
# calorie_range = sidebar.slider(
#   'Calorie Range',
#   0, 2000, (1000, 1500)
# )


#------------------------------------------------ activity level ---------------------------------##
activity_level = sidebar.selectbox(
  'Current Activity Level',
  ['Sedentary', 'Lightly active', 'Moderately active', 'Very active', 'Extra active'],
  index=None,
  placeholder="Choose an option",
  help='I know you are dumb. Sedentary = Lazy'
)


#-------------------------------------- Sidebar Submit button ------------------------------------##
generate_button = sidebar.button("Generate Meal Plan")

##_______________________________________________ St Meal Plan _____________________________________##

if generate_button:
  prompt = ( 
  "  Hi, My name is " + name + "I am a " + str(age) + " year old " + str(sex) + ". My height is " + str(height) + " (cm) and my weight is " + str(weight) + " (kg)."
  "  My current activity level is " + str(activity_level) + "." 
  "  Accessing all information I'm providing you, I want you to tell me what should be my recommended calorie intake for a day and create me a meal plan for 7 days.\n\n"
  "  Here is a list of ingredients I want to use: " + str(st.session_state.final_ingredient_list) +
  ". Here are my dietary restrictions: " + str(dietary_res) + 
  "  Here is my culinary preference : " + str(culinary_pref) + 
  "  Here are my allergies: " + str(allergies) + 
  "  Here is my health goals: " + str(health_goal) + 
  "In your response you must have these: "
  "   - Include breakfast, lunch, dinner, and snacks.\n"
  "   - Provide detailed recipes for each meal.\n"
  "   - Mention portion sizes and calorie counts for each meal.\n"
  "   - Consider variety and balance.\n\n"
  "  **Nutritional Considerations:**\n"
  "   - Calculate my recommended daily calorie intake based on the provided information.\n"
  "   - Ensure the meal plan meets my nutritional needs (vitamins, minerals, macronutrients).\n\n"
  "  **Extras:**\n"
  "   - If possible, suggest any supplements or superfoods that complement the meal plan.\n\n"
  "   Thank you! I look forward to receiving a detailed meal plan that covers all aspects, including recipes, nutritional value, and portion sizes."
)

  response = model.generate_content(prompt)

  # Store the meal plan in the session state
  st.session_state['meal_plan'] = response.text  

##___________________________________________ Download ________________________________________##
if 'meal_plan' in st.session_state:
  st.header("Hi " + name + "! Here is a 7-day meal plan tailored just for you...")
  st.write(st.session_state['meal_plan'])

  download_button = st.download_button(
    label="Download",
    data=st.session_state['meal_plan'].encode(),
    file_name="meal_plan.txt",
    mime="text/plain",
  )


