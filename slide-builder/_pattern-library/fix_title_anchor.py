import os, re, sys
sys.stdout.reconfigure(encoding='utf-8')

files = [f for f in os.listdir('.') if f.endswith('.html')]
target = []
for f in files:
    m = re.match(r'^(\d+)_', f)
    if m:
        n = int(m.group(1))
        if 281 <= n <= 351:
            target.append(f)
target.sort()

SKIP_PATTERNS = ['cover', 'divider', 'thank-you', 'closing-cta', 'pull-quote-interstitial', 'key-question-dark']

fixed_html = 0
skipped = 0
already_ok = 0

TITLE_CSS = {'position':'absolute','left':'64px','right':'64px','top':'28px','min-height':'36px'}
SUBHEAD_CSS = {'position':'absolute','left':'64px','right':'64px','top':'108px'}
RULE_CSS = {'position':'absolute','left':'64px','top':'136px','width':'56px','height':'3px'}
CONTAINER_CSS = {'position':'absolute','top':'0','left':'0','right':'0','height':'0','overflow':'visible'}


def replace_or_augment_class(text, cls, new_props):
    pattern = re.compile(r'(' + re.escape(cls) + r'\s*\{)([^}]*)(\})', re.DOTALL)
    def replacer(m):
        opening = m.group(1)
        old_props = m.group(2)
        closing = m.group(3)
        cleaned = old_props
        for prop in ['position','top','left','right','bottom',
                     'margin','margin-top','margin-bottom','margin-left','margin-right',
                     'padding','padding-top','padding-bottom','padding-left','padding-right',
                     'flex','flex-shrink','flex-grow','flex-direction',
                     'gap','align-items','justify-content','display',
                     'height','min-height','min-width','overflow']:
            cleaned = re.sub(r'[ \t]*' + re.escape(prop) + r'\s*:[^;\n]+[;\n]', '', cleaned)
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        new_lines = ['\n  ' + k + ': ' + v + ';' for k, v in new_props.items()]
        return opening + ''.join(new_lines) + cleaned + closing
    return pattern.sub(replacer, text, count=1)


def fix_html_file(fname):
    global fixed_html, skipped, already_ok

    name_lower = fname.lower()
    for skip in SKIP_PATTERNS:
        if skip in name_lower:
            print('  SKIP: ' + fname)
            skipped += 1
            return

    with open(fname, 'r', encoding='utf-8') as fp:
        content = fp.read()

    if re.search(r'\.action-title\s*\{[^}]*position:\s*absolute[^}]*top:\s*28px', content, re.DOTALL):
        print('  ALREADY_FIXED: ' + fname)
        already_ok += 1
        return

    original = content

    title_class = None
    for cls in ['.action-title', '.slide-title', '.title-line', '.title', '.header-title']:
        if cls == '.title':
            if re.search(r'\.title\s*\{[^}]*font-size:\s*2[0-9]px', content, re.DOTALL):
                title_class = cls; break
        else:
            if re.search(re.escape(cls) + r'\s*\{', content):
                title_class = cls; break

    subhead_class = None
    for cls in ['.subhead','.slide-subhead','.sub-headline','.slide-subtitle','.slide-subheadline']:
        if re.search(re.escape(cls) + r'\s*\{', content):
            subhead_class = cls; break

    rule_class = None
    for cls in ['.title-rule', '.accent-rule']:
        if re.search(re.escape(cls) + r'\s*\{', content):
            rule_class = cls; break

    container_class = None
    for cls in ['.title-block','.header-block','.title-band','.header','.slide-header','.title-zone']:
        if re.search(re.escape(cls) + r'\s*\{', content):
            container_class = cls; break

    print('  Processing: ' + fname)
    print('    title=' + str(title_class) + ' subhead=' + str(subhead_class) +
          ' rule=' + str(rule_class) + ' container=' + str(container_class))

    new_content = content
    made_changes = False

    if container_class and re.search(re.escape(container_class) + r'\s*\{', new_content):
        new_content = replace_or_augment_class(new_content, container_class, CONTAINER_CSS)
        made_changes = True

    if title_class and re.search(re.escape(title_class) + r'\s*\{', new_content):
        new_content = replace_or_augment_class(new_content, title_class, TITLE_CSS)
        made_changes = True

    if subhead_class and re.search(re.escape(subhead_class) + r'\s*\{', new_content):
        new_content = replace_or_augment_class(new_content, subhead_class, SUBHEAD_CSS)
        made_changes = True

    if rule_class == '.title-rule' and re.search(r'\.title-rule\s*\{', new_content):
        new_content = replace_or_augment_class(new_content, '.title-rule', RULE_CSS)
        made_changes = True
    elif rule_class == '.accent-rule':
        rule_matches = list(re.finditer(r'\.accent-rule\s*\{[^}]*\}', new_content, re.DOTALL))
        if len(rule_matches) == 1:
            new_content = replace_or_augment_class(new_content, '.accent-rule', RULE_CSS)
            made_changes = True
        else:
            print('    NOTE: multiple .accent-rule blocks - rule NOT repositioned')

    if not made_changes:
        print('    WARNING: no changes made')
        return
    if new_content == original:
        print('    NO CHANGE (patterns not matched)')
        return

    with open(fname, 'w', encoding='utf-8') as fp:
        fp.write(new_content)
    print('    FIXED: ' + fname)
    fixed_html += 1


for f in target:
    fix_html_file(f)

print('\n=== HTML SUMMARY: ' + str(fixed_html) + ' fixed, ' + str(already_ok) + ' already OK, ' + str(skipped) + ' skipped ===')
