import re,sys,html
sys.path.insert(0,'.')
from pipeline.facts import default_fetch
def text(url):
    s=default_fetch(url)
    s=re.sub(r'<(script|style)[^>]*>.*?</\1>',' ',s,flags=re.S)
    s=html.unescape(re.sub(r'<[^>]+>',' ',s)); return re.sub(r'\s+',' ',s)
if __name__=='__main__':
    t=text(sys.argv[1]); kws=sys.argv[2:]
    print(len(t))
    for k in kws:
        for m in list(re.finditer(k,t,re.I))[:3]:
            print('>>',k,'|',t[max(0,m.start()-120):m.end()+220]); print()
