from pyhwpx import Hwp
import pythoncom

HWP_TEMPLATE_PATH = "GSA_report_template.hwp"
HWP_SAVE_PATH = "GSA_report.hwp"

def generate(data, content):
    # open 
    pythoncom.CoInitialize()
    hwpx=Hwp(new=True) # , visible=False)
    hwpx.open(HWP_TEMPLATE_PATH) # , arg="suspendpassword:false;forceopen:true;versionwarning:false")

    # write page values
    hwpx.put_field_text("writer", data["writer"])

    hwpx.move_to_field("date1")
    hwpx.insert_text(data["date"].replace("-", "."))

    hwpx.move_to_field("date2")
    date_split=data["date"].split("-")
    hwpx.insert_text(date_split[0]+"년 "+date_split[1]+"월 "+date_split[2]+"일 "+data["day_of_week"])

    hwpx.move_to_field("location")
    hwpx.insert_text(data["location"])

    # create_table
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

    # write participants
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
    
    # write content
    hwpx.move_to_field(field="report_content")
    prev_level=0
    for block in content:
        if "text" in block and block["text"]!="":
            if block["text"]=="보고안건":
                hwpx.move_to_field(field="report_content")
                continue
            elif block["text"]=="논의안건":
                hwpx.DeleteBack()
                hwpx.move_to_field(field="discuss_content")
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
    
    # close with final save 
    hwpx.save_as(HWP_SAVE_PATH, arg="") 
    hwpx.clear()  # hwpx.clear(option=3)
    
    return HWP_SAVE_PATH