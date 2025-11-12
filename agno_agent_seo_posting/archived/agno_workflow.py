# Import requirements
from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.workflow import Step, Workflow, StepOutput, StepInput, Parallel
from agno.os import AgentOS
from pydantic import BaseModel, Field

## Reload functions module for updates
import re
import os
import importlib, functions_workflow
importlib.reload(functions_workflow) 

# Import functions
from dotenv import load_dotenv
load_dotenv()
# from functions_agent import export_docs_to_html
from functions_workflow import get_input_url_keyword
from functions_workflow import export_docs_to_html
from functions_workflow import slugify
from functions_workflow import extract_images_from_html_text
from functions_workflow import extract_h1_from_html_text
from functions_workflow import clean_html
from functions_workflow import create_an_empty_post
from functions_workflow import get_file_names
from functions_workflow import download_images
from functions_workflow import resize_image
from functions_workflow import upload_resized_image
from functions_workflow import update_new_src
from functions_workflow import process_html
from functions_workflow import get_html_template
from functions_workflow import clean_html_transformer
from functions_workflow import get_class_type
from functions_workflow import parse_function_block_one
from functions_workflow import upload_html_to_post
# Define list of docs url to run containing [{"url":  , "main_keyword": }]
docs_url_to_run=[]

# Define Pydantic model for structured output
class HTMLTransformerOutput(BaseModel):
    """Output model for HTML transformation function"""
    function_name: str = Field(
        description="The name of the transformation function (should be 'transform_html_to_template_format')"
    )
    function_code: str = Field(
        description="The complete Python function code as a string"
    )

# Frame of the workflow

html_template_agent = Agent(
        name = "HTML Agent",
        role = "Write code for changing the html",
        model = Claude(id="claude-sonnet-4-5-20250929", api_key=os.getenv("ANTHROPIC_API_KEY")),
        description="You are a html transformer. Base on a given html template string, you write code in python to modify any input html tags",
        instructions=[
            "When a html template string is given, read to make conclusions about the general format of each tag regrading <p, <img, ect.",
            "From that conclusions about the general form, write codes in python to modify tags of any input html to that general form using html = re.sub",
            "Assess all tags <p, <img, surroundings of <img, <ul, <li, <ol, <table, <tr, <td, <h2, <h3, <a, <strong, <em, make sure to go through all <tags",
            "for <p tags there are always two cases with text-align justify and center",
            "compose all codes as a function: def transform_html_to_template_format(html):",
            "Always remember to add needed library inside the def, for example import re"
            "return ONLY, SOLELY a dictionary containing the function name: transform_html_to_template_format and the whole function in function code:, no need summarization, nothing else, nothing."
        ],
        expected_output="""
        {example code: def transform_html_to_template_format(html): # 1. REMOVE <h1> tags: html = re.sub(r'<h1[^>]*>.*?</h1>', ' ', html, flags=re.IGNORECASE | re.DOTALL).strip()}
        """,
        tools = [],
        reasoning=True,
        # reasoning_max_steps=10,
        add_history_to_context=True, ## retrieve conversaion history -> memory
        # read_chat_history=True, ## enables agent to read the chat history that were previously stored
        # enable_session_summaries=True, ## summarizes the content of a long conversaion to storage
        # num_history_runs=2,
        # search_session_history=True, ## allow searching through past sessions
        # num_history_sessions=2, ## retrieve only the 2 lastest sessions of the agent
        markdown=True,
        debug_mode=True,
        cache_session=True
    )

agent_workflow = Workflow(
    name="Agent đăng bài SEO",
    steps=[
        Step(name="Get url and main keyword from users", executor=get_input_url_keyword),
        Step(name="Export docs to html format", executor=export_docs_to_html),
        Step(name="Extract <img tags", executor=extract_images_from_html_text),
        Step(name="Extract <h1 tags", executor=extract_h1_from_html_text),
        Step(name="Clean raw html ouput", executor=clean_html),
        Step(name="Slugify the main_keyword", executor=slugify),
        Step(name="Creating an empty post", executor=create_an_empty_post),
        Step(name="Get image file names", executor=get_file_names),
        Step(name="Download images", executor=download_images),
        Step(name="Resize downloaded images", executor=resize_image),
        Step(name="Upload resized images to Wordpress", executor=upload_resized_image),
        Step(name="Replace original src by new src", executor=update_new_src),
        Step(name="Get the html template", executor=get_html_template),
        Step(name="Get the html transformer", agent=html_template_agent),
        Step(name="Get the input_type",executor=get_class_type),
        Step(name="Clean the html transformer", executor=clean_html_transformer),
        Step(name="Turn a string into a dictionary", executor=parse_function_block_one),
        Step(name="Get the final html transformer function", executor=process_html),
        Step(name="Upload html to post",executor=upload_html_to_post)
        ]
)

# Replace the list below with your actual document URLs and keywords
docs_input = [
   {"url": "https://docs.google.com/document/d/1c2_xDkdte_NDmG3IJVHOE0-Np2-TeROoU7zwdAio0s8/edit?tab=t.0#heading=h.qaoui0zablj0", "main_keyword": "test", "html_template":"""<p dir="ltr" style="text-align: justify;"><span:...>Điều hòa công suất lớn là dòng máy cho phép một dàn nóng kết nối linh hoạt với nhiều dàn lạnh, thường ứng dụng trong hệ thống điều hòa VRF hiện đại. Giải pháp này đặc biệt phù hợp với các công trình quy mô lớn như tòa nhà văn phòng, khách sạn hay trung tâm thương mại nhờ khả năng làm mát mạnh mẽ, tiết kiệm diện tích và tối ưu hiệu suất vận hành. Dưới đây là TOP X+ mẫu điều hòa công suất lớn đáng đầu tư nhất năm 2025, đáp ứng tốt cả về chất lượng lẫn hiệu quả sử dụng.</p><table border="1"><colgroup><col /><col /><col /></colgroup><tbody><tr><td><p dir="ltr" style="text-align: center;"><strong>Tên sản phẩm</strong></p></td><td><p dir="ltr" style="text-align: center;"><strong>Hình ảnh</strong></p></td><td><p dir="ltr" style="text-align: center;"><strong>Điểm nổi bật</strong></p></td></tr><tr><td><p dir="ltr"><ahref="https://nagakawa.com.vn/dieu-hoa-trung-tam-mini-vrf-nagakawa-inverter-2-chieu-namu-h280u01-10hp">Điều hòa trung tâm Mini VRF Nagakawa Inverter 2 chiều NAMU-H280U01 10HP</a></p></td><td><p dir="ltr" style="text-align: center;"><img data-thumb="original" original-height="400" original-width="400" src="//bizweb.dktcdn.net/100/448/192/files/dieu-hoa-trung-tam-mini-vrf-nagakawa-inverter-2-chieu-namu-h280u01-10hp.png?v=1749109040442" /></p></td><td><p dir="ltr">Dòng máy mạnh nhất của Nagakawa Mini VRF, kết nối tới 15 dàn lạnh, phù hợp công trình lớn, vận hành bền bỉ trong môi trường khắc nghiệt.</p></td></tr><tr><td><p dir="ltr"><a href="https://nagakawa.com.vn/dieu-hoa-trung-tam-mini-vrf-nagakawa-inverter-2-chieu-namu-h224u01-8-5hp">Điều hòa trung tâm Mini VRF Nagakawa Inverter 2 chiều NAMU-H224U01 8.5HP</a></p></td><td><p dir="ltr" style="text-align: center;"><img data-thumb="original" original-height="400" original-width="400" src="//bizweb.dktcdn.net/100/448/192/files/dieu-hoa-trung-tam-mini-vrf-nagakawa-inverter-2-chieu-namu-h224u01-8-5hp.png?v=1749109067079" /></p></td><td><p dir="ltr">Tiết kiệm điện với công nghệ Inverter, tương thích đa dạng dàn lạnh, hoạt động êm và bền trong môi trường ẩm.</p></td></tr><tr><td><p dir="ltr"><a href="https://nagakawa.com.vn/dieu-hoa-trung-tam-mini-vrf-nagakawa-inverter-2-chieu-namu-h140u01-5-5hp">Điều hòa trung tâm Mini VRF Nagakawa Inverter 2 chiều NAMU-H140U01 5.5HP</a></p></td><td><p dir="ltr" style="text-align: center;"><img data-thumb="original" original-height="400" original-width="400" src="//bizweb.dktcdn.net/100/448/192/files/dieu-hoa-trung-tam-mini-vrf-nagakawa-inverter-2-chieu-namu-h140u01-5-5hp.png?v=1749109082789" /></p></td><td><p dir="ltr">Thiết kế nhỏ gọn, phù hợp nhà hàng – showroom, tự khởi động lại khi mất điện, chia tải công suất thông minh.</p></td></tr><tr><td><p dir="ltr"><a href="https://nagakawa.com.vn/dieu-hoa-trung-tam-mini-vrf-nagakawa-2-chieu-namu-h100u01-4hp">Điều hòa trung tâm Mini VRF Nagakawa Inverter 2 chiều NAMU-H100U01 4HP</a></p></td><td><p dir="ltr" style="text-align: center;"><img data-thumb="original" original-height="400" original-width="400" src="//bizweb.dktcdn.net/100/448/192/files/dieu-hoa-trung-tam-mini-vrf-nagakawa-inverter-2-chieu-namu-h100u01-4hp.png?v=1749109096284" /></p></td><td><p dir="ltr">Phù hợp homestay hoặc spa nhỏ, tiết kiệm điện, điều khiển trung tâm tiện lợi, quạt lớn vận hành êm.</p></td></tr><tr><td><p dir="ltr"><a href="https://nagakawa.com.vn/dieu-hoa-trung-tam-mini-vrf-nagakawa-inverter-2-chieu-namu-h160u01-6hp">Điều hòa trung tâm Mini VRF Nagakawa Inverter 2 chiều NAMU-H160U01 6HP</a></p></td><td><p dir="ltr" style="text-align: center;"><img data-thumb="original" original-height="400" original-width="400" src="//bizweb.dktcdn.net/100/448/192/files/dieu-hoa-trung-tam-mini-vrf-nagakawa-inverter-2-chieu-namu-h160u01-6hp.png?v=1749109109645" /></p></td><td><p dir="ltr">Chống ăn mòn cao, tương thích hệ thống BMS, tự điều chỉnh công suất theo tải sử dụng.</p></td></tr></tbody></table>...
"""}
]

agent_workflow.print_response(docs_input)
# html_tempalte_agent.print_response(input())