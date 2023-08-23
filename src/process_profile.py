from src.create_chrome_driver import create_chrome_driver

def process_profile(profile_index: int, profiles_dir:str, headless: bool = False) -> None:
  
    driver = create_chrome_driver(profile_index, user_data_dir=profiles_dir + "/profile" + str(profile_index))
    
    driver.get("https://www.instagram.com/")
    
    driver.close()
    
    