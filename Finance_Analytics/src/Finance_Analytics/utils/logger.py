
# The code is writen in /src/Finance_Analytics/__init__.py, as it will be available immediately for all modules within the Finance_Analytics package. You can access it in any file within the package by doing, "from Finance_Analytics import logger"

# While putting the logger in __init__.py can make it more readily available throughout your package, it's generally considered better practice to keep it in a dedicated module like utils/logger.py (i.e, this file). 
# This approach maintains better separation of concerns, allows for easier testing and modification of the logging setup, and keeps the __init__.py file cleaner and focused on package-level initialization.

# However, in this project we will not be testing the logging functionality in isolation so the code has be placed in src/Finance_Analytics/__init__.py.
# If you wish to test the logging functionality with higher isolation level, its recommended to copy the code here, and utilize "from src.Finance_Analytics import logger" instead of "from Finance_Analytics import logger"


