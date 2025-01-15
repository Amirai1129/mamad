import pymongo
from info import OTHER_DB_URI, DATABASE_NAME
from pyrogram import enums
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

myclient = pymongo.MongoClient(OTHER_DB_URI)
mydb = myclient[DATABASE_NAME]

# اضافه کردن یا بروزرسانی فیلتر
async def add_filter(grp_id, text, reply_text, btn, file, alert):
    mycol = mydb[str(grp_id)]
    data = {
        'text': str(text),
        'reply': str(reply_text),
        'btn': str(btn),
        'file': str(file),
        'alert': str(alert)
    }
    try:
        mycol.update_one({'text': str(text)}, {"$set": data}, upsert=True)
    except Exception as e:
        logger.exception('Some error occurred!', exc_info=True)

# جستجوی فیلترها
async def find_filter(group_id, name):
    mycol = mydb[str(group_id)]
    query = mycol.find({"text": {"$regex": name, "$options": "i"}})
    try:
        for file in query:
            reply_text = file['reply']
            btn = file['btn']
            fileid = file['file']
            alert = file.get('alert', None)
            return reply_text, btn, alert, fileid
    except Exception as e:
        logger.error(f"Error finding filter: {e}")
        return None, None, None, None

# دریافت تمام فیلترها
async def get_filters(group_id):
    mycol = mydb[str(group_id)]
    texts = []
    query = mycol.find()
    try:
        for file in query:
            texts.append(file['text'])
    except Exception as e:
        logger.error(f"Error getting filters: {e}")
    return texts

# حذف فیلتر
async def delete_filter(message, text, group_id):
    mycol = mydb[str(group_id)]
    myquery = {'text': text}
    query = mycol.count_documents(myquery)
    if query == 1:
        mycol.delete_one(myquery)
        await message.reply_text(
            f"'`{text}`' deleted. I'll not respond to that filter anymore.",
            quote=True,
            parse_mode=enums.ParseMode.MARKDOWN
        )
    else:
        await message.reply_text("Couldn't find that filter!", quote=True)

# حذف تمام فیلترها
async def del_all(message, group_id, title):
    if str(group_id) not in mydb.list_collection_names():
        await message.edit_text(f"Nothing to remove in {title}!")
        return
    mycol = mydb[str(group_id)]
    try:
        mycol.drop()
        await message.edit_text(f"All filters from {title} have been removed")
    except Exception as e:
        logger.error(f"Error deleting all filters: {e}")
        await message.edit_text("Couldn't remove all filters from group!")

# شمارش فیلترها
async def count_filters(group_id):
    mycol = mydb[str(group_id)]
    count = mycol.count_documents({})
    return False if count == 0 else count

# اطلاعات آماری فیلترها
async def filter_stats():
    collections = mydb.list_collection_names()
    if "CONNECTION" in collections:
        collections.remove("CONNECTION")
    totalcount = 0
    for collection in collections:
        mycol = mydb[collection]
        count = mycol.count_documents({})
        totalcount += count
    totalcollections = len(collections)
    return totalcollections, totalcount
