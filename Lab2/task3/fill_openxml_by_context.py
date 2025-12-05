import zipfile
import shutil
import os
from lxml import etree

INPUT_DOCX = "ПП.docx"          # исходный
OUTPUT_DOCX = "ПП_filled.docx"  # результат
TMP_DIR = "tmp_docx"



def unzip_docx(path, outdir):
    if os.path.exists(outdir):
        shutil.rmtree(outdir)
    os.makedirs(outdir)
    with zipfile.ZipFile(path, 'r') as z:
        z.extractall(outdir)

def zip_dir_to_docx(dirpath, outpath):
    with zipfile.ZipFile(outpath, 'w', zipfile.ZIP_DEFLATED) as z:
        for folder, _, files in os.walk(dirpath):
            for f in files:
                file_path = os.path.join(folder, f)
                archive_name = os.path.relpath(file_path, dirpath)
                z.write(file_path, archive_name)

def get_document_xml_path(tmp_dir):
    return os.path.join(tmp_dir, "word", "document.xml")

def collect_runs(tree, ns):
    return tree.findall('.//w:r', namespaces=ns)

def is_underlined_empty_run(r, ns):
    rPr = r.find('w:rPr', namespaces=ns)
    has_u = False
    if rPr is not None:
        u = rPr.find('w:u', namespaces=ns)
        if u is not None:
            has_u = True
    t = r.find('w:t', namespaces=ns)
    if has_u and (t is None or (t.text is None or t.text.strip() == "")):
        return True
    tab = r.find('w:tab', namespaces=ns)
    if has_u and tab is not None:
        return True
    return False

def run_contains_text(r, needle, ns):
    t = r.find('w:t', namespaces=ns)
    if t is None or t.text is None:
        return False
    return needle in t.text

def find_run_index_with_text(runs, needle, ns):
    for i, r in enumerate(runs):
        if run_contains_text(r, needle, ns):
            return i
    return -1

def find_next_underlined_index(runs, start_idx, ns):
    for i in range(start_idx + 1, len(runs)):
        if is_underlined_empty_run(runs[i], ns):
            return i
    return -1

def find_prev_contiguous_underlined_indices(runs, start_idx, ns, max_back=5):
    res = []
    i = start_idx - 1
    while i >= 0 and len(res) < max_back:
        if is_underlined_empty_run(runs[i], ns):
            res.insert(0, i)
            i -= 1
        else:
            break
    return res

def set_run_text_preserve_rPr(r, text, ns):
    rPr = r.find('w:rPr', namespaces=ns)
    for child in list(r):
        r.remove(child)
    if rPr is not None:
        r.append(rPr)
    t = etree.Element("{%s}t" % ns['w'])
    if text.startswith(" ") or text.endswith(" "):
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    t.text = text
    r.append(t)

def choose_side_of_slash_in_run(r, keep_left=True, ns=None):
    t = r.find('w:t', namespaces=ns)
    if t is None or t.text is None:
        return
    parts = t.text.split('/')
    if len(parts) < 2:
        return
    t.text = parts[0].strip() if keep_left else parts[1].strip()

def run_text(r, ns):
    t = r.find('w:t', namespaces=ns)
    return t.text if (t is not None and t.text is not None) else ""


def fill_by_context(document_xml_path, data):
    parser = etree.XMLParser(ns_clean=True, recover=True, encoding='utf-8')
    tree = etree.parse(document_xml_path, parser)
    root = tree.getroot()
    ns = root.nsmap
    if None in ns:
        ns['pkg'] = ns.pop(None)
    if 'w' not in ns:
        ns['w'] = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

    runs = collect_runs(tree, ns)

    # === Заполнение курса, группы, ФИО, даты, направления ===

    idx = find_run_index_with_text(runs, "Выдано студенту", ns)
    if idx != -1:
        next_u = find_next_underlined_index(runs, idx, ns)
        if next_u != -1:
            set_run_text_preserve_rPr(runs[next_u], f" {data['course']} ", ns)

    idx_g = find_run_index_with_text(runs, "группы", ns)
    if idx_g != -1:
        next_u = find_next_underlined_index(runs, idx_g, ns)
        if next_u != -1:
            set_run_text_preserve_rPr(runs[next_u], f" {data['group']} ", ns)

    idx_anchor = find_run_index_with_text(runs, "(фамилия, имя, отчество при наличии)", ns)
    if idx_anchor != -1:
        prev_indices = find_prev_contiguous_underlined_indices(runs, idx_anchor, ns, max_back=6)
        if prev_indices:
            first = prev_indices[0]
            set_run_text_preserve_rPr(runs[first], f" {data['student_name']} ", ns)
            for j in prev_indices[1:]:
                set_run_text_preserve_rPr(runs[j], " ", ns)

    idx_term = find_run_index_with_text(runs, "Срок прохождения практики", ns)
    if idx_term != -1:
        target_run = runs[idx_term]
        full_text = f"Срок прохождения практики: с {data['date_from']} по {data['date_to']}"
        set_run_text_preserve_rPr(target_run, full_text, ns)
        parent_p = target_run.getparent()
        all_runs_in_p = parent_p.findall("w:r", namespaces=ns)
        removing = False
        for r in all_runs_in_p:
            if removing:
                parent_p.remove(r)
            if r is target_run:
                removing = True

    for i, r in enumerate(runs):
        txt = run_text(r, ns)
        if "/" in txt and ("09.03.04" in txt or "38.03.05" in txt):
            keep_left = (data.get("direction_choice", "09.03.04") == "09.03.04")
            choose_side_of_slash_in_run(r, keep_left=keep_left, ns=ns)
            break

    for i, r in enumerate(runs):
        txt = run_text(r, ns)
        if "/" in txt and ("Научно-исследовательская" in txt or "Проектная" in txt):
            keep_left = (data.get("practice_type_choice", "Научно-исследовательская") == "Научно-исследовательская")
            choose_side_of_slash_in_run(r, keep_left=keep_left, ns=ns)
            break

    # Сохраняем изменения
    tree.write(document_xml_path, encoding='utf-8', xml_declaration=True)
    return True

# ----------------- Main -----------------

def main():
    if not os.path.exists(INPUT_DOCX):
        print(f"Файл {INPUT_DOCX} не найден.")
        return

    # --- Ввод данных пользователя ---
    values = {}
    values['student_name'] = input("Введите ФИО студента: ").strip()
    values['course'] = input("Введите курс студента: ").strip()
    values['group'] = input("Введите группу студента: ").strip()
    values['date_from'] = input("Введите дату начала практики (дд.мм.гггг): ").strip()
    values['date_to'] = input("Введите дату окончания практики (дд.мм.гггг): ").strip()

    # --- Выбор направления ---
    directions = {
        "1": "09.03.04",
        "2": "38.03.05"
    }
    print("Выберите направление практики:\n1 - 09.03.04\n2 - 38.03.05")
    choice = input("Ваш выбор (1/2): ").strip()
    values['direction_choice'] = directions.get(choice, "09.03.04")

    # --- Выбор типа практики ---
    practice_types = {
        "1": "Научно-исследовательская",
        "2": "Проектная"
    }
    print("Выберите тип практики:\n1 - Научно-исследовательская\n2 - Проектная")
    choice = input("Ваш выбор (1/2): ").strip()
    values['practice_type_choice'] = practice_types.get(choice, "Научно-исследовательская")

    unzip_docx(INPUT_DOCX, TMP_DIR)
    document_xml = get_document_xml_path(TMP_DIR)
    if not os.path.exists(document_xml):
        print("document.xml не найден в распакованной структуре.")
        return

    ok = fill_by_context(document_xml, values)
    if ok:
        zip_dir_to_docx(TMP_DIR, OUTPUT_DOCX)
        print("Поля заполнены:", OUTPUT_DOCX)
    else:
        print("Возникли проблемы при заполнении.")

    shutil.rmtree(TMP_DIR)

if __name__ == "__main__":
    main()
