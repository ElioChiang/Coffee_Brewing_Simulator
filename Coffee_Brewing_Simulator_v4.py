import streamlit as st


# Set page configuration for wider layout
st.set_page_config(layout="wide")

st.title("☕ 手沖咖啡參數模擬器")
st.markdown("探索不同沖煮參數、處理法與烘焙度對咖啡風味的影響。")
st.markdown("此模擬器僅供參考，實務上會因水質、濾杯、磨豆機不同而有所影響。")
st.markdown("👈 左側欄位可調整沖煮參數。")

# --- Default Parameters Configuration ---
DEFAULT_PARAMS = {
    "ratio": 15.0,
    "time": 150,
    "temperature": 90,
    "grind_size_index": 1,
    "process_method_index": 0,
    "roast_level_index": 1,
    "blooming_time": 30,
    "blooming_ratio": 2.0,
    "pour_count": 2,
}

# --- Session State Initialization ---
if 'initialized' not in st.session_state:
    for key, value in DEFAULT_PARAMS.items():
        st.session_state[key] = value
    st.session_state.initialized = True

# --- Reset Functionality ---
def reset_params():
    """Resets all parameters in session_state to their default values."""
    for key, value in DEFAULT_PARAMS.items():
        st.session_state[key] = value

# Place the reset button in the sidebar
st.sidebar.button("⚙️ 重置參數", on_click=reset_params)

# --- Sidebar Parameter Inputs ---
st.sidebar.header("請輸入沖煮參數")

# Options lists for widgets
grind_size_options = ["粗研磨 (海鹽狀)", "中等研磨 (砂糖狀)", "細研磨 (細砂糖狀)"]
process_method_options = ["水洗", "日曬", "蜜處理"]
roast_level_options = ["淺烘焙", "中烘焙", "深烘焙"]

# --- 基本沖煮參數 ---
st.sidebar.slider(
    "粉水比（1:X）", 10.0, 20.0,
    step=0.5,
    key='ratio',
    help="粉量與水量之比，影響咖啡濃度與風味強度。數字越小（如 1:13）咖啡越濃郁，數字越大（如 1:18）則越清淡。"
)
st.sidebar.slider(
    "總沖煮時間（秒）", 60, 240,
    step=10,
    key='time',
    help="水與咖啡粉接觸的總時間，影響萃取程度。時間過短可能導致萃取不足，過長則可能過度萃取產生雜味。"
)
st.sidebar.slider(
    "水溫（°C）", 80, 100,
    step=1,
    key='temperature',
    help="水溫高有助於更充分萃取，但過高易產生苦味；水溫低則萃取較慢，可能導致酸感突出或風味不足。"
)

selected_grind_size_str = st.sidebar.radio(
    "研磨度",
    grind_size_options,
    index=st.session_state.grind_size_index,
    key='grind_size_selector_widget',
    help="咖啡粉顆粒大小，是影響萃取速度和風味平衡的關鍵。細研磨增加接觸面積，萃取快；粗研磨則反之。"
)
st.session_state.grind_size_index = grind_size_options.index(selected_grind_size_str)
grind_size = selected_grind_size_str

selected_process_method_str = st.sidebar.selectbox(
    "處理法",
    process_method_options,
    index=st.session_state.process_method_index,
    key='process_method_selector_widget',
    help="咖啡生豆的處理方式，會對咖啡的風味輪廓產生基礎性影響。"
)
st.session_state.process_method_index = process_method_options.index(selected_process_method_str)
process_method = selected_process_method_str

selected_roast_level_str = st.sidebar.selectbox(
    "烘焙度",
    roast_level_options,
    index=st.session_state.roast_level_index,
    key='roast_level_selector_widget',
    help="咖啡豆的烘焙程度。淺烘焙強調產地特色和酸質；深烘焙則發展出更多焦糖、巧克力和醇厚度。"
)
st.session_state.roast_level_index = roast_level_options.index(selected_roast_level_str)
roast_level = selected_roast_level_str


# --- 專業模式參數 (現在將始終顯示) ---
st.sidebar.markdown("---") # 分隔線
st.sidebar.header("進階沖煮參數")

st.sidebar.slider(
    "悶蒸時間（秒）", 0, 60,
    step=5,
    key='blooming_time',
    help="咖啡粉與少量熱水接觸並釋放二氧化碳的階段。充足的悶蒸有助於咖啡粉均勻潤濕，提升後續萃取品質。"
)
blooming_time = st.session_state.blooming_time

st.sidebar.slider(
    "悶蒸水量（粉重倍數）", 1.5, 3.5,
    step=0.5,
    key='blooming_ratio',
    help="悶蒸時注入的水量相對於咖啡粉的重量。一般建議為咖啡粉的 2-3 倍重，水量不足或過多都會影響均勻萃取。"
)
blooming_ratio = st.session_state.blooming_ratio

st.sidebar.slider(
    "斷水次數", 0, 5,
    step=1,
    key='pour_count',
    help="多次分段注水（斷水）有助於控制萃取速度，發展更豐富的風味層次，減少過度萃取。"
)
pour_count = st.session_state.pour_count


# --- Flavor Calculation Function ---
@st.cache_data
def calculate_flavor_profile(ratio, time, temperature, grind_size, process_method, roast_level, blooming_time, blooming_ratio, pour_count): # 移除 mode 參數
    # Initial flavor baseline (these initial values can be adjusted)
    acid, sweet, bitter, body = 2.5, 2.5, 2.5, 2.5

    # Process Method Impact (Base adjustment)
    if process_method == "日曬":
        sweet += 1.5
        body += 1
        acid -= 0.5
        bitter -= 0.5
    elif process_method == "水洗":
        acid += 1.5
        body -= 0.5
        sweet -= 0.5
        bitter += 0.5
    elif process_method == "蜜處理":
        sweet += 1
        acid += 0.5
        body += 0.5

    # Roast Level Impact (Base adjustment, layered on top of process method)
    if roast_level == "淺烘焙":
        acid += 1.5
        sweet += 0.5
        bitter -= 1.5
        body -= 1
    elif roast_level == "深烘焙":
        bitter += 2
        body += 1.5
        sweet += 0.5
        acid -= 1.5

    # Basic Brewing Parameter Impact (Interacting with process method, roast level)
    # Grind Size & Time Interaction
    if grind_size == "細研磨 (細砂糖狀)":
        if time < 100:
            acid += 1.5
            bitter -= 1
            sweet -= 1
            body -= 1
        elif 100 <= time <= 180:
            sweet += 0.5
            body += 0.5
        else:
            bitter += 2
            acid -= 1.5
            sweet -= 1
            body += 1
    elif grind_size == "粗研磨 (海鹽狀)":
        if time < 120:
            acid += 1
            sweet -= 1.5
            body -= 1.5
        elif 120 <= time <= 180:
            pass
        else:
            sweet -= 1
            body -= 2
            bitter += 1
            acid += 0.5

    # Ratio Impact
    if ratio < 14:
        sweet += 0.5
        body += 0.5
        bitter += 0.5
    elif ratio > 17:
        acid += 0.5
        body -= 0.5
        sweet -= 0.5

    # Temperature Impact
    if temperature > 94:
        bitter += 1
        acid -= 0.5
        sweet -= 0.5
    elif temperature < 88:
        acid += 1.5
        sweet -= 1
        body -= 0.5
        bitter -= 0.5

    # Professional Mode Parameter Impact
    if blooming_time < 20 and blooming_time > 0:
        acid += 1
        body -= 1
        sweet -= 0.5
    elif blooming_time > 40:
        bitter += 1
        sweet -= 1
        acid -= 0.5
    elif blooming_time == 0: # 新增：若悶蒸時間為0，可能造成的影響
        acid += 0.5 # 未悶蒸可能導致萃取不均
        body -= 0.5
        sweet -= 0.5


    if blooming_ratio < 1.8:
        acid += 0.8
        sweet -= 0.8
        body -= 0.8
    elif blooming_ratio > 3.0:
        body -= 0.5
        bitter += 0.5

    if pour_count == 0:
        body -= 1
        sweet -= 1
        acid += 0.5
        bitter += 0.5
    elif pour_count >= 3:
        acid += 0.5
        bitter -= 0.5
        sweet += 0.5

    # Ensure all values are clamped between 0 and 5
    return (
        min(max(acid, 0), 5),
        min(max(sweet, 0), 5),
        min(max(bitter, 0), 5),
        min(max(body, 0), 5),
    )


# --- Flavor Description Function ---
@st.cache_data
def suggest_flavor_notes(acid, sweet, bitter, body, process_method, roast_level):
    notes = []

    # 1. Determine base flavor profile based on process method and roast level
    base_note = ""
    if process_method == "日曬":
        base_note = "**日曬處理**的咖啡，風味通常**醇厚、奔放**，帶有明顯的果實甜感"
    elif process_method == "水洗":
        base_note = "**水洗處理**的咖啡，風味通常**乾淨、明亮**"
    elif process_method == "蜜處理":
        base_note = "**蜜處理**的咖啡，風味介於水洗與日曬之間，通常具有**乾淨的甜感與平衡的酸質**"

    if roast_level == "淺烘焙":
        base_note += "，屬於**淺烘焙**，更能突顯**細緻的花果香與明亮酸質**。"
    elif roast_level == "中烘焙":
        base_note += "，屬於**中烘焙**，風味**平衡且豐富**，酸甜感適中，餘韻悠長。"
    elif roast_level == "深烘焙":
        base_note += "，屬於**深烘焙**，帶有**醇厚飽滿的可可、堅果與焦糖香氣**，苦甜平衡。"
    notes.append(f"此為{base_note}")

    # 2. Refine description based on the intensity of each flavor dimension
    # --- Acidity ---
    if acid >= 4:
        if roast_level == "淺烘焙" or process_method == "水洗":
            notes.append("- **高酸度：** 呈現**明亮、活潑的柑橘、檸檬**或**莓果**般的酸感，純淨且具穿透力，令人振奮。")
        elif roast_level == "中烘焙" or process_method == "蜜處理":
            notes.append("- **高酸度：** 多為**蘋果、葡萄**或**柔和柑橘**般的甜酸，圓潤且與甜感平衡，帶有回甘。")
        else:
            notes.append("- **高酸度：** 呈現**熱帶水果或熟成莓果**般的甜酸，多汁且與醇厚感融合，不尖銳。")
    elif acid >= 2:
        notes.append("- **中等酸度：** 酸質清晰且平衡，與其他風味和諧交織，不突兀。")
    else:
        notes.append("- **低酸度：** 酸質不明顯或柔和，口感平穩，可能更強調甜感或苦感。")

    # --- Sweetness ---
    if sweet >= 4:
        if roast_level == "淺烘焙" or process_method == "水洗":
            notes.append("- **高甜感：** 呈現**蔗糖、蜂蜜或花蜜**般的乾淨甜味，回甘明顯且持久。")
        elif process_method == "日曬" or process_method == "蜜處理":
            notes.append("- **高甜感：** 有著濃郁的**熱帶水果乾、莓果醬、焦糖或巧克力**般的香甜，醇厚且餘韻綿長。")
        else:
            notes.append("- **高甜感：** 甜感飽滿，如同**焦糖布丁或麥芽糖**般的醇厚甜味，與整體風味完美融合。")
    elif sweet >= 2:
        notes.append("- **中等甜感：：** 甜感平衡，能襯托其他風味，使口感更圓潤，增添舒適度。")
    else:
        notes.append("- **低甜感：** 甜感不足，咖啡風味可能顯得單薄或平淡，缺乏豐富性。")

    # --- Bitterness ---
    if bitter >= 4:
        if roast_level == "深烘焙":
            notes.append("- **高苦味：** 呈現**濃郁黑巧克力、可可**般的深沉苦感，或帶有**烘烤堅果、木質**氣息，若平衡得宜則有深度。")
        else:
            notes.append("- **高苦味：** 可能來自過度萃取，呈現不悅的**焦糊、煙燻或藥草**般的苦感，需調整參數。")
    elif bitter >= 2:
        notes.append("- **中等苦味：** 苦味適中，能增加咖啡的厚實感與層次，與甜感形成良好平衡。")
    else:
        notes.append("- **低苦味：** 苦味不明顯，整體風味可能更偏向酸甜感，口感較為清爽。")

    # --- Body ---
    if body >= 4:
        if process_method == "水洗":
            notes.append("- **高醇厚度：** 口感**滑順、乾淨**，像**絲綢般**的細膩質感，餘韻清爽而綿長。")
        elif process_method == "日曬" or roast_level == "深烘焙":
            notes.append("- **高醇厚度：** 口感**醇厚、黏稠**，像**奶油、糖漿般**的飽滿度，強勁且持久，充滿口腔。")
        else:
            notes.append("- **高醇厚度：** 口感**圓潤、中等偏厚**，有著良好的**黏稠感與質感**，提供豐富的口腔體驗。")
    elif body >= 2:
        notes.append("- **中等醇厚度：** 口感適中，既不單薄也不厚重，平衡舒適，順暢入喉。")
    else:
        notes.append("- **低醇厚度：** 口感清淡，可能顯得水感或單薄，餘韻較短，缺乏份量感。")

    # 3. Overall Balance Description
    if all(1.5 <= val <= 3.5 for val in [acid, sweet, bitter, body]):
        notes.append("☕ 整體風味**極為平衡且和諧**，各項風味元素融合得宜，口感舒適，展現出咖啡豆的純粹美好。")
    elif (acid > bitter and sweet > acid):
        notes.append("✨ 整體風味呈現良好的**酸甜平衡**，活潑的酸質與豐富的甜感相互輝映，餘韻迷人。")
    elif (bitter > acid and body > sweet):
        notes.append("🍫 整體風味醇厚，**苦甜感交織**，帶有厚實的口感和溫暖的風味，餘韻扎實。")

    return notes


# --- Adjustment Suggestions Function ---
@st.cache_data
def adjustment_tips(ratio, time, temperature, grind_size, blooming_time, blooming_ratio, pour_count):
    tips = []

    # Grind size and time interaction suggestions
    if grind_size == "細研磨 (細砂糖狀)":
        if time < 100:
            tips.append("📉 **風味尖銳/欠萃（細研磨+短時間）**：建議**延長總沖煮時間至 120-150 秒**，或稍微**調粗研磨度**，以避免萃取不足。")
        elif time > 180:
            tips.append("📈 **風味過苦/雜味（細研磨+長時間）**：這通常是過度萃取。建議**調粗研磨度**，或**縮短總沖煮時間至 150-180 秒**。")
    elif grind_size == "粗研磨 (海鹽狀)":
        if time < 120:
            tips.append("📉 **風味淡薄/水感（粗研磨+短時間）**：建議**調細研磨度**，或**延長總沖煮時間至 150-180 秒**，以提升萃取率。")
        elif 120 <= time <= 180:
            pass
        else:
            tips.append("📈 **風味稀薄/無層次（粗研磨+長時間）**：粗研磨長時間沖煮容易風味不佳。建議**調細研磨度**，並**控制在 120-180 秒內完成沖煮**。")
    else: # Medium grind
        if time < 120:
            tips.append("⏱️ **總沖煮時間偏短**：若風味清淡，可嘗試**延長總沖煮時間至 150-180 秒**，或稍微**調細研磨度**。")
        elif time > 180:
            tips.append("⏱️ **總沖煮時間偏長**：若風味有苦澀感，可嘗試**縮短總沖煮時間至 150-180 秒**，或稍微**調粗研磨度**。")

    if ratio < 14:
        tips.append("⚖️ **粉水比偏低（濃度高）**：若覺得咖啡過於濃郁或苦感重，建議**提升粉水比至 1:15～1:16**，有助於平衡甜感與醇厚度。")
    elif ratio > 17:
        tips.append("⚖️ **粉水比偏高（濃度低）**：若風味過淡或產生尖銳酸澀，建議**降低粉水比至 1:15～1:16**，讓咖啡風味更飽滿。")

    if temperature > 94:
        tips.append("🌡️ **水溫偏高**：若風味有明顯苦味或雜味，建議將水溫**降至 91～93°C**，有助於柔化苦感，突顯咖啡原有風味。")
    elif temperature < 88:
        tips.append("🌡️ **水溫偏低**：若風味清淡、酸感突出，建議將水溫**提升至 90°C 以上**，以充分萃取咖啡的甜感與香氣。")

    # 專業模式參數的建議
    if blooming_time < 20 and blooming_time > 0:
        tips.append("💧 **悶蒸時間不足**：建議**延長悶蒸時間至 30-40 秒**，充足的悶蒸有助於咖啡粉均勻吸水，提升整體萃取品質與甜感。")
    elif blooming_time > 40:
        tips.append("💧 **悶蒸時間過長**：可能導致咖啡粉過度悶蒸而產生苦澀。建議**縮短至 30-40 秒**。")
    elif blooming_time == 0:
        tips.append("💧 **未進行悶蒸**：強烈建議至少悶蒸 **30 秒**，這是均勻萃取和釋放咖啡香氣的關鍵步驟。")


    if blooming_ratio < 1.8:
        tips.append("💦 **悶蒸水量偏少**：建議**提升悶蒸水量至粉重的 2-3 倍**，以確保咖啡粉充分潤濕，避免萃取不均。")
    elif blooming_ratio > 3.0:
        tips.append("💦 **悶蒸水量偏多**：過多水分可能稀釋悶蒸效果。可考慮稍微**減少悶蒸水量至粉重的 2-3 倍**。")

    if pour_count == 0:
        tips.append("📈 **未斷水**：建議嘗試**至少 1-2 次斷水**，這有助於分段萃取，提升風味層次與飽滿度，減少過度萃取。")
    elif pour_count >= 3:
        tips.append("📉 **斷水次數較多**：若風味過於複雜或酸度突出，可考慮**減少斷水次數至 2 次**，或調整注水方式讓水流更平穩。")

    if not tips:
        tips.append("👍 **參數配置良好！** 您目前的沖煮參數看起來很平衡。若想進一步優化，可嘗試**微調研磨度**或**變化注水手法**來探索更細緻的風味。")
    return tips

st.markdown("---")
# --- Simulation Results Display Section ---
st.subheader("模擬結果")

# 使用 st.session_state 來獲取所有參數
acid, sweet, bitter, body = calculate_flavor_profile(
    st.session_state.ratio,
    st.session_state.time,
    st.session_state.temperature,
    grind_size,
    process_method,
    roast_level,
    blooming_time,
    blooming_ratio,
    pour_count
)

st.markdown("#### 📊 風味強度預測")

# --- 使用單一的窄欄位來包含所有進度條，使其垂直顯示但更短 ---
# 這裡創建了兩個欄位，第一個欄位用於進度條，第二個用於填充空白。
# 0.3 代表第一個欄位佔總寬度的 30%。你可以調整這個值來控制進度條的長度。
progress_col, _ = st.columns([0.5, 0.5])

with progress_col:
    st.write(f"**酸度**")
    st.progress(acid / 5)
    st.write(f"**甜感**")
    st.progress(sweet / 5)
    st.write(f"**苦味**")
    st.progress(bitter / 5)
    st.write(f"**醇厚度**")
    st.progress(body / 5)
# --- 結束 columns 區塊 ---


st.markdown("#### 📜 可能風味敘述")
notes = suggest_flavor_notes(acid, sweet, bitter, body, process_method, roast_level)
for note in notes:
    st.markdown(f"- {note}")

st.markdown("---")

st.markdown("#### 📌 建議調整方向")
tips = adjustment_tips(
    st.session_state.ratio,
    st.session_state.time,
    st.session_state.temperature,
    grind_size,
    blooming_time,
    blooming_ratio,
    pour_count
)
for tip in tips:
    st.markdown(f"{tip}")

st.markdown("---")

# --- Coffee Basic Knowledge Section ---
st.subheader("💡 咖啡沖煮小知識")
# --- 使用單一的窄欄位來包含所有小知識的 expender ---
# 這裡設定為 0.6，表示佔總寬度的 60%。你可以調整這個值。
knowledge_col, _ = st.columns([0.6, 0.4])

with knowledge_col:
    with st.expander("什麼是咖啡沖煮的四大變因？"):
        st.markdown("""
        咖啡沖煮的風味主要受以下四大變因影響，它們相互作用：
        * **研磨度 (Grind Size)：** 咖啡粉顆粒的大小。越細的粉接觸面積越大，萃取越快；越粗的粉萃取越慢。
        * **粉水比 (Brew Ratio)：** 咖啡粉與水的比例。影響咖啡的濃度與風味強度，是決定咖啡「濃淡」的關鍵。
        * **水溫 (Water Temperature)：** 沖煮時水溫的高低。高溫有助於快速萃取，但也易帶出苦澀；低溫則萃取較慢，可能導致酸感突出或風味不足。
        * **沖煮時間 (Brew Time)：** 水與咖啡粉接觸的總時間。水與咖啡粉接觸的總時間，影響萃取程度。時間過短可能導致萃取不足，過長則可能過度萃取產生雜味。
        """)

    with st.expander("悶蒸 (Bloom) 的重要性？"):
        st.markdown("""
        悶蒸是沖煮咖啡的第一步，通常是將少量熱水（約咖啡粉重量的2-3倍）注入咖啡粉中，使其完全濕潤，並靜置約20-40秒。
        * **作用：** 讓咖啡粉中的二氧化碳排出，避免影響後續萃取。同時，讓咖啡粉均勻潤濕，為後續的均勻萃取打下基礎。
        * **影響：** 悶蒸不足可能導致風味不均、酸澀；悶蒸過度則可能風味平淡或帶有悶味。
        """)

    with st.expander("為什麼要斷水？"):
        st.markdown("""
        斷水（或分段注水）是指在總沖煮過程中，將水量分成幾次注入，每次注入後停止注水一段時間，讓水流自然滴落。
        * **作用：** 有助於更精確地控制萃取過程，可以發展出更豐富的風味層次、提升甜感，並減少過度萃取的風險。同時也能幫助新手更容易掌握沖煮節奏。
        * **影響：** 適當的斷水能讓風味更清晰、飽滿；完全不斷水（一次性注水）可能導致萃取不均或風味扁平。
        """)

    with st.expander("水洗、日曬、蜜處理有什麼差別？"):
        st.markdown("""
        這是咖啡生豆的處理方式，直接影響咖啡豆的最終風味：
        * **水洗處理 (Washed/Wet Process)：** 咖啡果實去皮去果肉後，將生豆放入水中發酵，再清洗、乾燥。風味通常**乾淨、明亮、酸質突出**，更能展現產地特色。
        * **日曬處理 (Natural/Dry Process)：** 咖啡果實直接帶著果肉在陽光下乾燥，待乾燥後再去皮去果肉。風味通常**醇厚、甜感飽滿、帶有明顯的發酵果香**，如莓果、熱帶水果風味。
        * **蜜處理 (Honey Process)：** 介於水洗和日曬之間。去皮後保留部分果膠層（Mucilage）進行乾燥。依保留果膠的量和處理時間，又分黃蜜、紅蜜、黑蜜等。風味通常具有**乾淨的甜感、平衡的酸質與良好的醇厚度**，風味豐富且甜感優雅。
        """)

    with st.expander("烘焙度如何影響咖啡風味？"):
        st.markdown("""
        烘焙度決定了咖啡豆的化學變化和風味發展：
        * **淺烘焙 (Light Roast)：** 豆子內部發展輕微，保留更多原始風味。風味通常**酸質明亮、花香、果香、柑橘調**突出，口感較輕盈。
        * **中烘焙 (Medium Roast)：** 豆子發展均衡，酸甜苦醇厚度達到良好平衡。風味常有**堅果、焦糖、巧克力**等調性，口感圓潤，層次豐富。
        * **深烘焙 (Dark Roast)：** 豆子發展度高，許多原始酸質和花果香會被烘焙風味取代。風味通常有**濃郁的煙燻、焦糖、烘烤、黑巧克力**等苦甜感，醇厚度高，口感強勁。
        """)
# --- 結束 columns 區塊 ---