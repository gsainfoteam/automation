import dotenv, os
from notion_client import Client

dotenv.load_dotenv()
client = Client(auth=os.getenv("NOTION_TOKEN"))

def _get_data(page):
    data = {}
    data["participants"] = []

    participants=page["properties"]["참여자"]["people"]
    for participant in participants:
        data["participants"].append("홍길동") ### ((participant["name"]))  # 오류 방지 테스트용 주석 
    data["participants_num"]=len(data["participants"])

    data["title"] = page["properties"]["제목"]["title"][0]["plain_text"]
    # writer=client.users.retrieve(page["properties"]["Author"]["people"][0]["id"]) #TODO: edit to adopt to the origin doc's format
    # data["writer"] = writer["name"]
    data["writer"] = "홍길동" ### page["properties"]["회의록 작성자"]["people"][0]["name"]  # 오류 방지 테스트용 주석 
    data["location"] = "윙방" ### page["properties"]["회의 장소"]["rich_text"][0]["text"]["content"]  # 오류 방지 테스트용 주석 
    data["date"]=page["properties"]["날짜"]["date"]["start"]
    data["day_of_week"] = page["properties"]["요일포함 날짜"]["formula"]["string"][-3:]

    return data

def _get_blocks(block_id):
    raw_content = client.blocks.children.list(block_id)
    for block in raw_content["results"]:
        if block["has_children"]:
            block["children"] = _get_blocks(block["id"])
    return raw_content

def _parse_block(block):
    block_type = block["type"]
    block_data = block[block_type]
    if block_type == "image":
        return {"type": block_type, "source": block_data["file"]["url"]}
    elif block_type=="link_to_page":
        return {"type": block_type, "text": ""}
    return {
        "type": block_type,
        "text": "".join(map(lambda b: b["plain_text"], block_data["rich_text"])),
    }

def _parse_content(blocks, indent=0):
    result = []
    for block in blocks:
        if block["type"] in ["column", "column_list", "divider"]:
            continue
        result.append(
            {
                **_parse_block(block),
                "indent": indent,
            }
        )
        if block["has_children"]:
            result.extend(
                _parse_content(block["children"]["results"], indent=indent + 1)
            )
    return result

def get(notion_pageid): 
    page = client.pages.retrieve(notion_pageid) 
    data = _get_data(page) 
    raw_content = _get_blocks(notion_pageid) 
    content = _parse_content(raw_content["results"])
    
    return data, content 
    