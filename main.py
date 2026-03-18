import os 
from dotenv import load_dotenv
import bot 

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
ForumId = int(os.getenv("FORUM_ID"))
MemberRoleId = int(os.getenv("MEMBER_ROLE_ID"))

if __name__ == "__main__":
    bot