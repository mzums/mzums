import requests

def get_xkcd():
    url = "https://xkcd.com/info.0.json"
    try:
        res = requests.get(url)
        if res.status_code == 200:
            data = res.json()
            title = data['safe_title']
            img_url = data['img']
            alt = data['alt']
            link = f"https://xkcd.com/{data['num']}"
            return f"![{title}]({img_url})\n\n[{title}]({link}) — *{alt}*"
        else:
            return "⚠️ Could not fetch XKCD."
    except Exception as e:
        return f"⚠️ Error: {e}"

def replace_section(content, marker, new_value):
    start = f"<!--{marker}:START-->"
    end = f"<!--{marker}:END-->"
    if start not in content or end not in content:
        print(f"Warning: markers {start} or {end} not found in README.md")
        return content
    pre = content.split(start)[0]
    post = content.split(end)[1]
    return f"{pre}{start}\n{new_value}\n{end}{post}"


with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

readme = replace_section(readme, "XKCD", get_xkcd())

with open("README.md", "w", encoding="utf-8") as f:
    f.write(readme)
