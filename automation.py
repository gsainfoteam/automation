# %% setup
from dotenv import load_dotenv
import os
from notion_client import Client
import json
from pyhwpx import Hwp

load_dotenv()
hwpx=Hwp()

# %% get page
client = Client(auth=os.getenv("NOTION_TOKEN"))
page = client.pages.retrieve(os.getenv("PAGE"))
page

# %% get blocks
def get_blocks(block_id=os.getenv("PAGE")):
    content = client.blocks.children.list(block_id)
    for block in content["results"]:
        if block["has_children"]:
            block["children"] = get_blocks(block["id"])
    return content


content = get_blocks()
content

# %% set data
data = {}
data["participants"] = []

participants=page["properties"]["참여자"]["people"]
for participant in participants:
    data["participants"].append((participant["name"]))
data["participants_num"]=len(data["participants"])

data["title"] = page["properties"]["제목"]["title"][0]["plain_text"]
# writer=client.users.retrieve(page["properties"]["Author"]["people"][0]["id"]) #TODO: edit to adopt to the origin doc's format
# data["writer"] = writer["name"]
data["writer"] = page["properties"]["회의록 작성자"]["people"][0]["name"]
data["location"] = page["properties"]["회의 장소"]["multi_select"][0]["name"]
data["date"]=page["properties"]["날짜"]["date"]["start"]
data["day_of_week"] = page["properties"]["요일포함 날짜"]["formula"]["string"][-3:]

data

#%% write page values
hwpx.put_field_text("writer", data["writer"])

hwpx.move_to_field("date1")
hwpx.insert_text(data["date"].replace("-", "."))

hwpx.move_to_field("date2")
date_split=data["date"].split("-")
hwpx.insert_text(date_split[0]+"년 "+date_split[1]+"월 "+date_split[2]+"일 "+data["day_of_week"])

# hwpx.move_to_field("location")
# hwpx.insert_text(data["location"])

# %% create_table
hwpx.move_to_field("participants")
for _ in range(data["participants_num"]//2-1):
    hwpx.TableAppendRow()
    hwpx.TableLowerCell()
if len(data["participants"])%2==1:
    for _ in range(2):
        hwpx.TableRightCell()
    for _ in range(3):
        hwpx.TableRightCell()
        hwpx.TableCellBorderDiagonalDown()


# %% write participants
hwpx.move_to_field("participants")
num=1
for i in range((data["participants_num"]//2)+data["participants_num"]%2):
    name=data["participants"][i]
    hwpx.insert_text(str(num))
    hwpx.TableRightCell()
    hwpx.insert_text(name)
    hwpx.TableRightCell()
    if name=="최익준":
        hwpx.insert_text("정보국장")
    elif name!="최익준":
        hwpx.insert_text("정보국원")

    for _ in range(2):
        hwpx.TableLeftCell()
    hwpx.TableLowerCell()
    num+=1

hwpx.move_to_field("participants")
for _ in range(3): hwpx.TableRightCell()
for i in range((data["participants_num"]//2)+data["participants_num"]%2, data["participants_num"]):
    name=data["participants"][i]
    hwpx.insert_text(str(num))
    hwpx.TableRightCell()
    hwpx.insert_text(name)
    hwpx.TableRightCell()
    if name=="최익준":
        hwpx.insert_text("정보국장")
    elif name!="최익준":
        hwpx.insert_text("정보국원")

    for _ in range(2):
        hwpx.TableLeftCell()
    hwpx.TableLowerCell()
    num+=1

# %% set content


def parse_data(block):
    block_type = block["type"]
    block_data = block[block_type]
    if block_type == "image":
        return {"type": block_type, "source": block_data["file"]["url"]}
    print(block)
    return {
        "type": block_type,
        "text": "".join(map(lambda b: b["plain_text"], block_data["rich_text"])),
    }

unsupported=["column", "column_list", "divider", "synced_block", "unsupported", "table_of_contents", "link_to_page", "link_preview", "file"]
def parse_content(blocks=content["results"], indent=0):
    result = []
    for block in blocks:
        if block["type"] in unsupported:
            continue
        result.append(
            {
                **parse_data(block),
                "indent": indent,
            }
        )
        if block["has_children"]:
            result.extend(
                parse_content(block["children"]["results"], indent=indent + 1)
            )
    return result


parse_content()



# %% write content
prev_level=0
cur_level=0
ignore=False
for block in parse_content():
    if "text" in block and block["text"]!="":
        if block["text"]=="보고 안건":
            hwpx.move_to_field(field="report_content")
            continue
        elif block["text"]=="논의 안건":
            hwpx.DeleteBack()
            hwpx.move_to_field(field="discuss_content")
            continue
        elif block["text"]=="<ignore>":
            ignore=True
        elif block["text"]=="</ignore>":
            ignore=False
            continue
        if ignore:
            continue
        
        if block["type"]=="heading_1" or block["type"]=="heading_2":
            cur_level=0
        elif block["type"]=="heading_3":
            cur_level=1
        elif block["indent"]==0:
            cur_level=2
        elif block["indent"]==1:
            cur_level=3
        elif block["indent"]==2:
            cur_level=4
        elif block["indent"]==3:
            cur_level=5
        
        if prev_level-cur_level<0:
            for _ in range(cur_level-prev_level):
                hwpx.HAction.Run("ParaNumberBulletLevelDown")
        elif prev_level-cur_level>0:
            for _ in range(prev_level-cur_level):
                hwpx.HAction.Run("ParaNumberBulletLevelUp")
        
        hwpx.insert_text(block["text"])
        hwpx.BreakPara()
    elif "text" not in block:
        continue
    prev_level=cur_level
hwpx.DeleteBack()

# %%


# %%
