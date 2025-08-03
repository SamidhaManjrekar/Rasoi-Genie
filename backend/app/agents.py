# agents.py - Place this file in your FastAPI project directory (same level as main.py)

from langchain.agents import AgentType, create_react_agent, AgentExecutor
from langchain.tools import Tool
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from typing import Dict, List, Any
import json
import random
from datetime import datetime, timedelta

class IndianMenuDatabase:
    """Simulated database of Indian dishes - replace with actual DB queries later"""
    
    DISHES = {
        "north_indian": {
            "breakfast": {
                "veg": ["Aloo Paratha", "Chole Bhature", "Poha", "Upma", "Idli Sambhar", "Masala Dosa"],
                "non_veg": ["Egg Paratha", "Keema Paratha", "Chicken Sandwich"],
                "vegan": ["Poha", "Upma", "Vegetable Dalia", "Ragi Dosa"]
            },
            "lunch": {
                "veg": ["Dal Tadka + Roti", "Rajma + Rice", "Chole + Rice", "Palak Paneer + Roti", 
                       "Bhindi Masala + Roti", "Aloo Gobi + Roti", "Mix Veg + Roti"],
                "non_veg": ["Chicken Curry + Rice", "Mutton Curry + Roti", "Fish Curry + Rice"],
                "vegan": ["Dal Tadka + Roti", "Chana Masala + Rice", "Vegetable Curry + Roti"]
            },
            "dinner": {
                "veg": ["Paneer Butter Masala + Roti", "Dal Makhani + Rice", "Stuffed Paratha + Raita"],
                "non_veg": ["Butter Chicken + Naan", "Lamb Biryani", "Fish Fry + Rice"],
                "vegan": ["Mixed Dal + Roti", "Vegetable Biryani", "Stuffed Roti + Pickle"]
            },
            "snacks": {
                "veg": ["Samosa", "Pakora", "Dhokla", "Kachori", "Sandwich"],
                "non_veg": ["Chicken Tikka", "Seekh Kebab", "Egg Roll"],
                "vegan": ["Bhel Puri", "Roasted Chana", "Fruit Chaat"]
            }
        },
        "south_indian": {
            "breakfast": {
                "veg": ["Idli Sambhar", "Masala Dosa", "Uttapam", "Rava Upma", "Medu Vada"],
                "non_veg": ["Egg Dosa", "Chicken 65"],
                "vegan": ["Plain Dosa", "Coconut Rice", "Lemon Rice"]
            },
            "lunch": {
                "veg": ["Sambhar Rice", "Rasam Rice", "Curd Rice", "Vegetable Curry + Rice"],
                "non_veg": ["Fish Curry + Rice", "Chicken Curry + Rice", "Mutton Biryani"],
                "vegan": ["Sambhar Rice", "Tamarind Rice", "Coconut Chutney + Rice"]
            },
            "dinner": {
                "veg": ["Paneer Masala + Rice", "Mixed Vegetable Curry + Rice"],
                "non_veg": ["Chicken Biryani", "Fish Fry + Rice"],
                "vegan": ["Vegetable Biryani", "Dal Rice"]
            },
            "snacks": {
                "veg": ["Murukku", "Banana Chips", "Coconut Laddu"],
                "non_veg": ["Chicken 65", "Fish Fry"],
                "vegan": ["Roasted Groundnuts", "Coconut Barfi"]
            }
        },
        "gujarati": {
            "breakfast": {
                "veg": ["Dhokla", "Khandvi", "Thepla", "Fafda Jalebi", "Poha"],
                "vegan": ["Plain Thepla", "Dhokla", "Khakhra"]
            },
            "lunch": {
                "veg": ["Dal Dhokli", "Undhiyu", "Gujarati Kadhi + Rice", "Bhindi Shaak + Rotli"],
                "vegan": ["Mixed Dal + Rotli", "Vegetable Curry + Rice"]
            },
            "dinner": {
                "veg": ["Gujarati Thali", "Khichdi Kadhi", "Stuffed Paratha"],
                "vegan": ["Simple Khichdi", "Vegetable Curry + Rotli"]
            },
            "snacks": {
                "veg": ["Dhokla", "Kachori", "Chakri", "Sev Mamra"],
                "vegan": ["Khakhra", "Roasted Chana"]
            }
        },
        "marathi": {
            "breakfast": {
                "veg": ["Poha", "Upma", "Misal Pav", "Sabudana Khichdi", "Thalipeeth"],
                "vegan": ["Poha", "Upma", "Sabudana Khichdi"]
            },
            "lunch": {
                "veg": ["Dal Rice", "Bharleli Vangi", "Alu Vadi", "Zunka Bhakar"],
                "vegan": ["Dal Rice", "Vegetable Curry + Rice"]
            },
            "dinner": {
                "veg": ["Puran Poli", "Bhakri + Pitla", "Vegetable Curry + Rice"],
                "vegan": ["Simple Dal + Rice", "Vegetable Curry + Bhakri"]
            },
            "snacks": {
                "veg": ["Vada Pav", "Bhel Puri", "Kothimbir Vadi"],
                "vegan": ["Bhel Puri", "Roasted Chana"]
            }
        },
        "bengali": {
            "breakfast": {
                "veg": ["Luchi Aloo Dum", "Poha", "Cholar Dal + Luchi"],
                "non_veg": ["Fish Curry + Rice", "Egg Curry + Luchi"],
                "vegan": ["Poha", "Aloo Dum + Rice"]
            },
            "lunch": {
                "veg": ["Dal Rice", "Aloo Posto", "Begun Bhaja + Rice"],
                "non_veg": ["Fish Curry + Rice", "Chicken Curry + Rice", "Prawn Malai Curry"],
                "vegan": ["Dal Rice", "Aloo Posto + Rice"]
            },
            "dinner": {
                "veg": ["Khichuri", "Mixed Vegetable + Rice"],
                "non_veg": ["Fish Curry + Rice", "Mutton Curry + Rice"],
                "vegan": ["Simple Khichuri", "Dal Rice"]
            },
            "snacks": {
                "veg": ["Jhal Muri", "Beguni", "Ghugni"],
                "non_veg": ["Fish Fry", "Chicken Cutlet"],
                "vegan": ["Jhal Muri", "Roasted Chana"]
            }
        },
        "punjabi": {
            "breakfast": {
                "veg": ["Chole Bhature", "Aloo Paratha", "Sarson da Saag + Makki Roti"],
                "non_veg": ["Keema Paratha", "Egg Paratha"],
                "vegan": ["Plain Paratha", "Sarson da Saag + Makki Roti"]
            },
            "lunch": {
                "veg": ["Dal Makhani + Naan", "Rajma + Rice", "Palak Paneer + Roti"],
                "non_veg": ["Butter Chicken + Naan", "Mutton Curry + Rice"],
                "vegan": ["Chana Masala + Rice", "Mixed Dal + Roti"]
            },
            "dinner": {
                "veg": ["Paneer Tikka Masala + Naan", "Dal Tadka + Rice"],
                "non_veg": ["Chicken Tikka Masala + Naan", "Lamb Curry + Rice"],
                "vegan": ["Mixed Vegetable + Roti", "Dal Rice"]
            },
            "snacks": {
                "veg": ["Samosa", "Pakora", "Kulcha"],
                "non_veg": ["Chicken Tikka", "Seekh Kebab"],
                "vegan": ["Chana Chaat", "Fruit Chaat"]
            }
        }
    }
    
    NUTRITIONAL_BALANCE = {
        "high_protein": ["Dal", "Paneer", "Chicken", "Fish", "Egg", "Chana", "Rajma"],
        "high_fiber": ["Bhindi", "Palak", "Mixed Veg", "Salad", "Gobi", "Begun"],
        "low_oil": ["Steamed", "Boiled", "Grilled", "Idli", "Upma"],
        "diabetic_friendly": ["Dal", "Vegetables", "Grilled items", "Salad", "Upma", "Poha"]
    }

class MenuGenerationTools:
    """Tools for the LangChain agent to use"""
    
    def __init__(self):
        self.db = IndianMenuDatabase()
    
    def get_dishes_by_criteria(self, cuisine: str, meal_type: str, diet_type: str, count: int = 5) -> List[str]:
        """Get dishes based on cuisine, meal type, and diet preference"""
        try:
            dishes = self.db.DISHES.get(cuisine, {}).get(meal_type, {}).get(diet_type, [])
            return random.sample(dishes, min(count, len(dishes))) if dishes else []
        except Exception as e:
            return []
    
    def check_nutritional_balance(self, dishes: List[str], health_conditions: List[str]) -> Dict[str, Any]:
        """Check if the meal plan is nutritionally balanced"""
        balance_score = 0
        recommendations = []
        
        # Check for protein sources
        protein_dishes = [dish for dish in dishes if any(protein in dish for protein in self.db.NUTRITIONAL_BALANCE["high_protein"])]
        if len(protein_dishes) >= 2:
            balance_score += 25
        else:
            recommendations.append("Add more protein sources like Dal, Paneer, or Chicken")
        
        # Check for fiber sources
        fiber_dishes = [dish for dish in dishes if any(fiber in dish for fiber in self.db.NUTRITIONAL_BALANCE["high_fiber"])]
        if len(fiber_dishes) >= 3:
            balance_score += 25
        else:
            recommendations.append("Include more vegetables like Bhindi, Palak, or Mixed Vegetables")
        
        # Check for variety
        if len(set(dishes)) == len(dishes):  # All unique dishes
            balance_score += 25
        else:
            recommendations.append("Ensure variety - avoid repeating similar dishes")
        
        # Health condition considerations
        if "diabetes" in health_conditions:
            diabetic_friendly = [dish for dish in dishes if any(friendly in dish for friendly in self.db.NUTRITIONAL_BALANCE["diabetic_friendly"])]
            if len(diabetic_friendly) >= len(dishes) * 0.6:
                balance_score += 25
            else:
                recommendations.append("Choose more diabetic-friendly options like Dal and Vegetables")
        else:
            balance_score += 25
        
        return {
            "balance_score": balance_score,
            "recommendations": recommendations,
            "is_balanced": balance_score >= 75
        }
    
    def generate_grocery_list(self, weekly_menu: Dict) -> Dict[str, List[str]]:
        """Generate grocery list from weekly menu"""
        grocery_categories = {
            "vegetables": [],
            "grains_pulses": [],
            "dairy_proteins": [],
            "spices_condiments": [],
            "others": []
        }
        
        # Simple ingredient mapping (expand this based on your needs)
        ingredient_mapping = {
            "Dal": ("grains_pulses", ["Toor Dal", "Moong Dal", "Masoor Dal"]),
            "Paneer": ("dairy_proteins", ["Paneer", "Milk"]),
            "Chicken": ("dairy_proteins", ["Chicken"]),
            "Rice": ("grains_pulses", ["Basmati Rice"]),
            "Roti": ("grains_pulses", ["Wheat Flour"]),
            "Bhindi": ("vegetables", ["Bhindi (Okra)"]),
            "Aloo": ("vegetables", ["Potatoes"]),
            "Palak": ("vegetables", ["Spinach"]),
            "Gobi": ("vegetables", ["Cauliflower"]),
            "Fish": ("dairy_proteins", ["Fresh Fish"]),
            "Egg": ("dairy_proteins", ["Eggs"]),
            "Chole": ("grains_pulses", ["Chickpeas"]),
            "Rajma": ("grains_pulses", ["Kidney Beans"])
        }
        
        all_dishes = []
        for day_menu in weekly_menu.values():
            all_dishes.extend(day_menu.values())
        
        for dish in all_dishes:
            for ingredient, (category, items) in ingredient_mapping.items():
                if ingredient in dish:
                    grocery_categories[category].extend(items)
        
        # Remove duplicates
        for category in grocery_categories:
            grocery_categories[category] = list(set(grocery_categories[category]))
        
        return grocery_categories

class IndianMenuAgent:
    """Main agent class for generating Indian meal plans"""
    
    def __init__(self, openai_api_key: str):
        self.openai_api_key = openai_api_key
        try:
            self.llm = ChatOpenAI(
                temperature=0.7,
                model="gpt-3.5-turbo",
                openai_api_key=openai_api_key
            )
        except Exception as e:
            print(f"Warning: Could not initialize OpenAI client: {e}")
            self.llm = None
            
        self.tools_handler = MenuGenerationTools()
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True) if self.llm else None
        self.tools = self._create_tools() if self.llm else []
        self.agent_executor = self._create_agent() if self.llm else None
    
    def _create_tools(self) -> List[Tool]:
        """Create tools for the agent"""
        return [
            Tool(
                name="get_dishes_by_criteria",
                description="Get dishes based on cuisine, meal type, and diet preference. Input: 'cuisine,meal_type,diet_type,count'",
                func=lambda x: str(self.tools_handler.get_dishes_by_criteria(*x.split(",")[:3], int(x.split(",")[3]) if len(x.split(",")) > 3 else 5))
            ),
            Tool(
                name="check_nutritional_balance",
                description="Check nutritional balance of dishes and health conditions. Input: 'dish1,dish2,dish3|health_condition1,health_condition2'",
                func=lambda x: str(self._parse_balance_input(x))
            ),
            Tool(
                name="generate_grocery_list",
                description="Generate grocery list from weekly menu. Input: JSON string of weekly menu",
                func=lambda x: str(self.tools_handler.generate_grocery_list(json.loads(x)))
            )
        ]
    
    def _parse_balance_input(self, input_str: str) -> Dict:
        """Parse input for nutritional balance check"""
        parts = input_str.split("|")
        dishes = parts[0].split(",") if parts[0] else []
        health_conditions = parts[1].split(",") if len(parts) > 1 and parts[1] else []
        return self.tools_handler.check_nutritional_balance(dishes, health_conditions)
    
    def _create_agent(self) -> AgentExecutor:
        """Create the main agent executor"""
        
        prompt_template = """
        You are an expert Indian cuisine meal planner. Your goal is to create balanced, diverse, and delicious weekly meal plans.
        
        You have access to the following tools:
        {tools}
        
        Use the following format:
        Question: the input question you must answer
        Thought: you should always think about what to do
        Action: the action to take, should be one of [{tool_names}]
        Action Input: the input to the action
        Observation: the result of the action
        ... (this Thought/Action/Action Input/Observation can repeat N times)
        Thought: I now know the final answer
        Final Answer: the final answer to the original input
        
        Remember:
        1. Ensure variety - don't repeat the same dish multiple times in a week
        2. Balance nutrition - include proteins, vegetables, and grains
        3. Consider health conditions when selecting dishes
        4. Respect dietary preferences (veg/non-veg/vegan)
        5. Include dishes from preferred cuisines
        6. Suggest balanced meals for each day
        
        Question: {input}
        Thought: {agent_scratchpad}
        """
        
        prompt = PromptTemplate.from_template(prompt_template)
        
        agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            max_iterations=10,
            handle_parsing_errors=True
        )
    
    def generate_weekly_menu(self, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a weekly menu based on user preferences"""
        
        if not self.agent_executor:
            # Use fallback if agent is not available
            return self._fallback_menu_generation(preferences)
        
        # Prepare the prompt for the agent
        prompt = f"""
        Create a 7-day meal plan with the following preferences:
        - Diet Type: {preferences.get('diet_type')}
        - Cuisines: {', '.join(preferences.get('cuisine', []))}
        - Meals: {', '.join(preferences.get('meals', []))}
        - Cooking Time: {preferences.get('cooking_time')}
        - Health Conditions: {', '.join(preferences.get('health_conditions', []))}
        
        For each day (Monday to Sunday), suggest:
        {', '.join(preferences.get('meals', []))}
        
        Ensure:
        1. No dish repeats in the entire week
        2. Nutritionally balanced meals
        3. Variety in cooking methods and ingredients
        4. Consideration for health conditions
        5. Appropriate for the specified diet type
        
        Return the response in this JSON format:
        {{
            "Monday": {{"breakfast": "dish_name", "lunch": "dish_name", "dinner": "dish_name"}},
            "Tuesday": {{"breakfast": "dish_name", "lunch": "dish_name", "dinner": "dish_name"}},
            ... for all 7 days
        }}
        
        Also provide nutritional balance analysis and any recommendations.
        """
        
        try:
            response = self.agent_executor.invoke({"input": prompt})
            return self._parse_agent_response(response["output"], preferences)
        except Exception as e:
            print(f"Error in agent execution: {e}")
            return self._fallback_menu_generation(preferences)
    
    def _parse_agent_response(self, response: str, preferences: Dict) -> Dict[str, Any]:
        """Parse agent response and structure it properly"""
        try:
            # Try to extract JSON from the response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx]
                menu_data = json.loads(json_str)
            else:
                raise ValueError("No JSON found in response")
            
            return {
                "menu": menu_data,
                "preferences_used": preferences,
                "generated_at": datetime.now().isoformat(),
                "agent_response": response
            }
        except Exception as e:
            print(f"Error parsing agent response: {e}")
            return self._fallback_menu_generation(preferences)
    
    def _fallback_menu_generation(self, preferences: Dict) -> Dict[str, Any]:
        """Fallback menu generation if agent fails"""
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        fallback_menu = {}
        
        diet_type = preferences.get('diet_type', 'veg')
        cuisines = preferences.get('cuisine', ['north_indian'])
        meals = preferences.get('meals', ['breakfast', 'lunch', 'dinner'])
        
        used_dishes = set()
        
        for day in days:
            fallback_menu[day] = {}
            for meal in meals:
                dish_found = False
                for cuisine in cuisines:
                    dishes = self.tools_handler.get_dishes_by_criteria(cuisine, meal, diet_type, 20)
                    available_dishes = [dish for dish in dishes if dish not in used_dishes]
                    
                    if available_dishes:
                        selected_dish = random.choice(available_dishes)
                        fallback_menu[day][meal] = selected_dish
                        used_dishes.add(selected_dish)
                        dish_found = True
                        break
                
                if not dish_found:
                    # If no dish found, use a generic option
                    fallback_menu[day][meal] = f"Simple {meal.title()} ({diet_type})"
        
        return {
            "menu": fallback_menu,
            "preferences_used": preferences,
            "generated_at": datetime.now().isoformat(),
            "fallback_used": True,
            "message": "Generated using fallback system"
        }