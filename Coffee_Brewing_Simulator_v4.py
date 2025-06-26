import streamlit as st


st.title("☕ 咖啡沖煮參數模擬器")
st.markdown("模擬不同參數與處理法下，可能產生的風味與建議調整方向")

# 模式切換
mode = st.sidebar.radio("請選擇模式", ["普通模式", "專業模式 | 悶蒸、斷水"])

st.sidebar.header("請輸入沖煮參數")

ratio = st.sidebar.slider("粉水比（1:X）", 10.0, 20.0, 15.0, 0.5)
time = st.sidebar.slider("總沖煮時間（秒）", 60, 240, 150, 10)
temperature = st.sidebar.slider("水溫（°C）", 80, 100, 90, 1)
grind_size = st.sidebar.radio("研磨度", ["粗研磨", "中等研磨", "細研磨"], index=1)
process_method = st.sidebar.selectbox("處理法", ["水洗", "日曬", "蜜處理"])

# 專業模式獨有參數
blooming_time = 0
pour_count = 0
if mode == "專業模式 | 悶蒸、斷水":
    blooming_time = st.sidebar.slider("悶蒸時間（秒）", 0, 60, 30, 5)
    pour_count = st.sidebar.slider("斷水次數", 0, 5, 2, 1)


def calculate_flavor_profile(ratio, time, temperature, grind_size, process_method, blooming_time=0, pour_count=0):
    acid, sweet, bitter, body = 3, 3, 2, 2

    # 基本參數影響
    if grind_size == "細研磨" and time > 180: # 細研磨 + 長時間 -> 過度萃取
        bitter += 2
        acid -= 1
    elif grind_size == "粗研磨" and time < 120: # 粗研磨 + 短時間 -> 萃取不足
        sweet -= 1
        body -= 1
    elif grind_size == "粗研磨" and time > 180: # 新增：粗研磨 + 長時間 -> 稀薄、欠萃酸
        sweet -= 1
        body -= 2
        acid += 1
    elif grind_size == "細研磨" and time < 100: # 新增：細研磨 + 短時間 -> 尖銳酸
        acid += 2
        bitter -= 1
        sweet -= 1


    if ratio < 14: # 粉量相對較多
        sweet += 1
        body += 1
    elif ratio > 17: # 粉量相對較少
        acid += 1
        body -= 1

    if temperature > 94: # 高水溫
        bitter += 1
        acid -= 1
    elif temperature < 88: # 低水溫
        acid += 1
        sweet -= 1

    # 處理法影響
    if process_method == "日曬":
        sweet += 1.5 # 日曬甜感更強
        body += 1
        acid -= 0.5 # 酸度可能被甜感掩蓋或較不突出
    elif process_method == "水洗":
        acid += 1.5 # 水洗強調酸質與乾淨度
        body -= 0.5 # 相對清爽
    elif process_method == "蜜處理":
        sweet += 1
        acid += 0.5 # 甜感提升，同時保有一定酸質


    # 專業模式參數影響
    if mode == "專業模式 | 悶蒸、斷水":
        if blooming_time < 20: # 悶蒸時間不足
            acid += 1
            body -= 1
        elif blooming_time > 40: # 悶蒸時間過長
            bitter += 1
            sweet -= 1

        if pour_count == 0: # 無斷水
            body -= 1
            sweet -= 1
            acid += 0.5 # 萃取不均可能導致欠萃酸
        elif pour_count >= 3: # 斷水次數較多
            acid += 0.5 # 提升層次與酸質呈現
            bitter -= 0.5 # 減少苦味萃取，或使苦味更平衡
            sweet += 0.5 # 甜感可能更佳


    return (
        min(max(acid, 0), 5),
        min(max(sweet, 0), 5),
        min(max(bitter, 0), 5),
        min(max(body, 0), 5),
    )


def suggest_flavor_notes(acid, sweet, bitter, body, process_method):
    notes = []

    # 1. 根據處理法決定基礎風味基調
    if process_method == "水洗":
        notes.append("此為**水洗處理**的咖啡，整體風味通常**乾淨、明亮**。")
    elif process_method == "日曬":
        notes.append("此為**日曬處理**的咖啡，整體風味通常**醇厚、奔放**，帶有明顯的果實甜感。")
    elif process_method == "蜜處理":
        notes.append("此為**蜜處理**的咖啡，風味介於水洗與日曬之間，通常具有**乾淨的甜感與平衡的酸質**。")

    # 2. 根據各風味維度的強度來細化描述
    # --- 酸度 ---
    if acid >= 4:
        if process_method == "水洗":
            notes.append("- **高酸度：** 呈現**明亮、活潑的柑橘、檸檬**酸感，或像**綠茶**般清爽，純淨且具穿透力。")
        elif process_method == "日曬":
            notes.append("- **高酸度：** 多為**莓果（草莓、藍莓）或熱帶水果**般的甜酸，圓潤且多汁，與甜感相輔相成。")
        elif process_method == "蜜處理":
            notes.append("- **高酸度：** 常見於**蘋果、葡萄**或**柔和柑橘**般的酸質，酸甜平衡，伴隨回甘。")
    elif acid >= 2: # 中等酸度
        if process_method == "水洗":
            notes.append("- **中等酸度：** 酸質清晰，可能帶有**輕盈的柑橘或堅果調**，整體平衡。")
        elif process_method == "日曬":
            notes.append("- **中等酸度：** 酸質柔和，融入整體果香與甜感中，不突兀。")
        elif process_method == "蜜處理":
            notes.append("- **中等酸度：** 酸質圓潤，與甜感交織，呈現**焦糖化的水果**風味。")
    else: # 低酸度或酸度不明顯
        notes.append("- **低酸度：** 酸質不明顯或被其他風味掩蓋，口感可能較為平穩或偏苦。")

    # --- 甜感 ---
    if sweet >= 4:
        if process_method == "水洗":
            notes.append("- **高甜感：** 呈現**蔗糖、焦糖**般的乾淨甜味，或**花蜜般**的細膩回甘，餘韻綿長。")
        elif process_method == "日曬":
            notes.append("- **高甜感：** 有著濃郁的**熱帶水果乾、莓果醬、蜂蜜、楓糖漿**般的香甜，醇厚且持久。")
        elif process_method == "蜜處理":
            notes.append("- **高甜感：** 常見於**熟果、焦糖、蜂蜜**般的甜感，通常帶有良好的一致性與黏稠度，回甘明顯。")
    elif sweet >= 2: # 中等甜感
        notes.append("- **中等甜感：** 甜感平衡，能襯托其他風味，使口感更圓潤。")
    else: # 低甜感
        notes.append("- **低甜感：** 甜感不足，咖啡風味可能顯得單薄或平淡。")

    # --- 苦味 ---
    if bitter >= 4:
        if process_method == "水洗":
            notes.append("- **高苦味：** 可能來自過度萃取，呈現**烘烤堅果、濃郁黑巧克力**的深沉苦感，或帶有**藥草、木質**氣息。")
        elif process_method == "日曬":
            notes.append("- **高苦味：** 有時伴隨**烘烤味、重可可**的複雜感，若處理不當可能出現**土味或發酵味**。")
        elif process_method == "蜜處理":
            notes.append("- **高苦味：** 多為**可可、焦糖**般的醇厚苦味，若與甜感平衡則能增加深度。")
    elif bitter >= 2: # 中等苦味
        notes.append("- **中等苦味：** 苦味適中，能增加咖啡的厚實感與層次，不顯突兀。")
    else: # 低苦味
        notes.append("- **低苦味：** 苦味不明顯，整體風味可能更偏向酸甜感，口感較清爽。")

    # --- 厚度（Body）---
    if body >= 4:
        if process_method == "水洗":
            notes.append("- **高厚度：** 口感**滑順、乾淨**，像**絲綢般**的細膩質感，餘韻清爽而綿長。")
        elif process_method == "日曬":
            notes.append("- **高厚度：** 口感**醇厚、黏稠**，像**奶油、糖漿般**的飽滿度，強勁且持久，充滿口腔。")
        elif process_method == "蜜處理":
            notes.append("- **高厚度：** 口感**圓潤、中等偏厚**，有著良好的**黏稠感與質感**，提供豐富的口腔體驗。")
    elif body >= 2: # 中等厚度
        notes.append("- **中等厚度：** 口感適中，既不單薄也不厚重，平衡舒適。")
    else: # 低厚度
        notes.append("- **低厚度：** 口感清淡，可能顯得水感或單薄，餘韻較短。")

    # 3. 綜合平衡性描述 (僅在沒有任何一個風味特別突出時顯示)
    if not any([acid >= 4, sweet >= 4, bitter >= 4, body >= 4]):
        if process_method == "水洗":
            notes.append("整體風味**極為平衡、清爽與乾淨**，酸甜苦厚度完美融合，展現出咖啡豆純粹且高雅的風味。")
        elif process_method == "日曬":
            notes.append("整體風味**和諧、豐富**，帶有溫和的果香甜感，口感圓潤，層次感佳。")
        elif process_method == "蜜處理":
            notes.append("整體風味**完美平衡、柔和**，甜感與酸質融合得宜，口感滑順，餘韻甜美而持久。")

    return notes


# 確保 adjustment_tips 函數在使用前被定義
def adjustment_tips(ratio, temperature, blooming_time=0, pour_count=0, mode="普通模式"):
    tips = []
    if ratio < 14:
        tips.append("✔ 建議提升粉水比至 1:15～1:16 以增加甜感與厚度")
    elif ratio > 17:
        tips.append("✔ 粉水比偏高，建議降低至 1:15～1:16 以避免風味過淡或產生酸澀")
    if temperature > 94:
        tips.append("✔ 水溫偏高，建議降至 91～93°C 以避免過苦")
    elif temperature < 88:
        tips.append("✔ 水溫偏低，建議提升至 90°C 以上強化萃取")

    if mode == "專業模式":
        if blooming_time < 20:
            tips.append("✔ 悶蒸時間不足，建議延長至 30-40 秒，有助於均勻萃取並提升甜感")
        elif blooming_time > 40:
            tips.append("✔ 悶蒸時間過長，可能導致過度萃取產生苦味，建議縮短至 30-40 秒")
        if pour_count == 0:
            tips.append("✔ 建議嘗試至少 1-2 次斷水，有助於分段萃取，提升風味層次")
        elif pour_count >= 3:
            tips.append("✔ 斷水次數較多，若風味過於複雜或酸度突出，可考慮減少斷水次數或調整注水方式")

    if not tips:
        tips.append("✔ 參數配置良好，可嘗試微調研磨度微調風味")
    return tips


st.subheader("📝 模擬結果")

acid, sweet, bitter, body = calculate_flavor_profile(
    ratio, time, temperature, grind_size, process_method, blooming_time, pour_count
)

st.markdown("**風味強度預測**")
for label, value in [("酸度", acid), ("甜感", sweet), ("苦味", bitter), ("厚度（Body）", body)]:
    st.write(label)
    st.progress(value / 5)



st.markdown("**可能風味敘述**")
# 將 process_method 傳入 suggest_flavor_notes
notes = suggest_flavor_notes(acid, sweet, bitter, body, process_method)
for note in notes:
    st.markdown(f"{note}") # 使用 f-string 直接輸出，省去 - 號讓排版更自然

st.markdown("---") # 加入分隔線，使排版更清晰
st.markdown("**📌 建議調整**")
for tip in adjustment_tips(ratio, temperature, blooming_time, pour_count, mode):
    st.write(f"- {tip}") # 使用 f-string 保持一致性