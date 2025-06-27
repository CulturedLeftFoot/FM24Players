import streamlit as st
import pandas as pd
import re
import requests
from urllib.parse import urlencode

# Load credentials from secrets.toml
CLIENT_ID = st.secrets["client_id"]
CLIENT_SECRET = st.secrets["client_secret"]
BOT_TOKEN = st.secrets["bot_token"]
GUILD_ID = st.secrets["guild_id"]
ALLOWED_ROLE_IDS = st.secrets["allowed_roles"]

AUTH_URL = st.secrets["auth_url"]
TOKEN_URL = st.secrets["token_url"]
USER_URL = st.secrets["user_url"]
REDIRECT_URI = "https://fm24players.streamlit.app"

st.set_page_config(page_title="Player Role Matcher", layout="wide")
st.title("⚽ Player Role Matching Dashboard")

def get_login_url():
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": "identify guilds guilds.members.read"
    }
    return f"{AUTH_URL}?{urlencode(params)}"

def exchange_code_for_token(code):
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "scope": "identify guilds guilds.members.read"
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    return requests.post(TOKEN_URL, data=data, headers=headers).json()

def get_user_info(token):
    headers = {"Authorization": f"Bearer {token}"}
    return requests.get(USER_URL, headers=headers).json()

def get_user_roles(user_id):
    headers = {"Authorization": f"Bot {BOT_TOKEN}"}
    url = f"https://discord.com/api/guilds/{GUILD_ID}/members/{user_id}"
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        return res.json().get("roles", [])
    return []

query_params = st.query_params

if "access_token" not in st.session_state:
    if "code" not in query_params:
        login_url = get_login_url()
        if st.button("🔐 Login with Discord"):
            st.markdown(f"<script>window.location.href = '{login_url}';</script>", unsafe_allow_html=True)
            st.stop()
    else:
        token_data = exchange_code_for_token(query_params["code"][0])
        access_token = token_data.get("access_token")
        if "access_token" in token_data:
            access_token = token_data["access_token"]
            user = get_user_info(access_token)
            user_roles = get_user_roles(user["id"])

            if any(role in ALLOWED_ROLE_IDS for role in user_roles):
                st.session_state["access_token"] = access_token
                st.session_state["user"] = user
                st.success(f"✅ Welcome {user['username']}#{user['discriminator']}")
            else:
                st.error("🚫 You do not have access to use this tool.")
                st.stop()
        else:
            st.error("❌ Failed to authenticate with Discord. Here’s the full response:")
            st.json(token_data)  # <-- THIS shows you what Discord returned
            st.stop()
    
else:
    user = st.session_state["user"]
    st.info(f"Logged in as {user['username']}#{user['discriminator']}")

# Upload HTML file
uploaded_file = st.file_uploader("Upload your SquadAnalysis HTML file", type=["html"])

if uploaded_file:
    try:
        tables = pd.read_html(uploaded_file)
        attributes_df = tables[0]  # Use the first table found
        attributes_df.columns = attributes_df.columns.str.strip()
    except Exception as e:
        st.error(f"Failed to read HTML table: {e}")
        st.stop()

    # Load formulas
    formula_text = """
    # (Paste your entire long formula string here, unchanged)
    
AF At = ((((Attributes[Dri]+Attributes[Fin]+Attributes[Fir]+Attributes[Tec]+Attributes[OtB]+Attributes[Cmp]+Attributes[Acc])/7)*0.8)+(((Attributes[Pas]+Attributes[Ant]+Attributes[Dec]+Attributes[Wor]+Attributes[Agi]+Attributes[Bal]+Attributes[Pac]+Attributes[Sta])/8)*0.2))+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4)*0.1)

DLF At = ((((Attributes[Fir]+Attributes[Pas]+Attributes[Tec]+Attributes[Cmp]+Attributes[Dec]+Attributes[OtB]+Attributes[Tea])/7)*0.8)+(((Attributes[Fin]+Attributes[Ant]+Attributes[Fla]+Attributes[Vis]+Attributes[Bal]+Attributes[Str]+Attributes[Dri])/7)*0.2))+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4)*0.1)

DLF Su = ((((Attributes[Fir]+Attributes[Pas]+Attributes[Tec]+Attributes[Cmp]+Attributes[Dec]+Attributes[OtB]+Attributes[Tea])/7)*0.8)+(((Attributes[Fin]+Attributes[Ant]+Attributes[Fla]+Attributes[Vis]+Attributes[Bal]+Attributes[Str])/6)*0.2))+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4)*0.1)

CF At = ((((Attributes[Dri]+Attributes[Fir]+Attributes[Hea]+Attributes[Tec]+Attributes[Ant]+Attributes[Cmp]+Attributes[OtB]+Attributes[Acc]+Attributes[Agi]+Attributes[Str]+Attributes[Fin])/11)*0.8)+(((Attributes[Vis]+Attributes[Tea]+Attributes[Wor]+Attributes[Bal]+Attributes[Pas]+Attributes[Lon]+Attributes[Jum]+Attributes[Pac]+Attributes[Sta]+Attributes[Dec])/10)*0.2))+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4)*0.1)

CF Su = ((((Attributes[Dri]+Attributes[Fir]+Attributes[Hea]+Attributes[Lon]+Attributes[Pas]+Attributes[Tec]+Attributes[Ant]+Attributes[Cmp]+Attributes[Dec]+Attributes[OtB]+Attributes[Vis]+Attributes[Acc]+Attributes[Agi]+Attributes[Str])/14)*0.8)+(((Attributes[Fin]+Attributes[Tea]+Attributes[Wor]+Attributes[Bal]+Attributes[Jum]+Attributes[Pac]+Attributes[Sta])/7)*0.2))+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4)*0.1)

TF At = ((((Attributes[Hea]+Attributes[Bra]+Attributes[Tea]+Attributes[Bal]+Attributes[Jum]+Attributes[Str]+Attributes[Fin]+Attributes[Cmp])/8)*0.8)+(((Attributes[Fir]+Attributes[Agg]+Attributes[Ant]+Attributes[Dec]+Attributes[OtB])/5)*0.2))+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4)*0.1)

TF Su = ((((Attributes[Hea]+Attributes[Bra]+Attributes[Tea]+Attributes[Bal]+Attributes[Jum]+Attributes[Str])/6)*0.8)+(((Attributes[Fin]+Attributes[Fir]+Attributes[Agg]+Attributes[Ant]+Attributes[Cmp]+Attributes[Dec]+Attributes[OtB])/7)*0.2))+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4)*0.1)

Poach At = ((((Attributes[Fin]+Attributes[Ant]+Attributes[Cmp]+Attributes[OtB])/4)*0.8)+(((Attributes[Fir]+Attributes[Hea]+Attributes[Tec]+Attributes[Dec]+Attributes[Acc])/5)*0.2))+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4)*0.1)

Pre Fwd At = ((((Attributes[Agg]+Attributes[Ant]+Attributes[Bra]+Attributes[Dec]+Attributes[Tea]+Attributes[Wor]+Attributes[Acc]+Attributes[Pac]+Attributes[Sta])/9)*0.8)+(((Attributes[Fir]+Attributes[Cmp]+Attributes[Cnt]+Attributes[Agi]+Attributes[Bal]+Attributes[Str]+Attributes[OtB]+Attributes[Fin])/8)*0.2))+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4)*0.1)

Pre Fwd Su = ((((Attributes[Agg]+Attributes[Ant]+Attributes[Bra]+Attributes[Dec]+Attributes[Tea]+Attributes[Wor]+Attributes[Acc]+Attributes[Pac]+Attributes[Sta])/9)*0.8)+(((Attributes[Fir]+Attributes[Cmp]+Attributes[Cnt]+Attributes[Agi]+Attributes[Bal]+Attributes[Str]+Attributes[OtB]+Attributes[Pas])/8)*0.2))+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4)*0.1)

Pre Fwd De = ((((Attributes[Agg]+Attributes[Ant]+Attributes[Bra]+Attributes[Dec]+Attributes[Tea]+Attributes[Wor]+Attributes[Acc]+Attributes[Pac]+Attributes[Sta])/9)*0.8)+(((Attributes[Fir]+Attributes[Cmp]+Attributes[Cnt]+Attributes[Agi]+Attributes[Bal]+Attributes[Str])/6)*0.2))+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4)*0.1)

F9 Su = (((((Attributes[Dri]+Attributes[Fir]+Attributes[Pas]+Attributes[Tec]+Attributes[Cmp]+Attributes[Dec]+Attributes[OtB]+Attributes[Vis]+Attributes[Acc]+Attributes[Agi])/10)*0.8)+(((Attributes[Fin]+Attributes[Ant]+Attributes[Fla]+Attributes[Tea]+Attributes[Bal])/5)*0.2)))+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4)*0.1)

IF A = ((((Attributes[Dri]+Attributes[Fin]+Attributes[Fir]+Attributes[Tec]+Attributes[OtB]+Attributes[Acc]+Attributes[Agi])/7)*0.8)+(((Attributes[Lon]+Attributes[Pas]+Attributes[Ant]+Attributes[Cmp]+Attributes[Fla]+Attributes[Wor]+Attributes[Bal]+Attributes[Pac]+Attributes[Sta])/9)*0.2))+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4*0.1))

IF S = ((((Attributes[Dri]+Attributes[Fin]+Attributes[Fir]+Attributes[Tec]+Attributes[OtB]+Attributes[Acc]+Attributes[Agi])/7)*0.8)+(((Attributes[Lon]+Attributes[Pas]+Attributes[Ant]+Attributes[Cmp]+Attributes[Fla]+Attributes[Vis]+Attributes[Wor]+Attributes[Bal]+Attributes[Pac]+Attributes[Sta])/10)*0.2))+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4*0.1))

Wide Mid At = ((((Attributes[Pas]+Attributes[Tck]+Attributes[Tea]+Attributes[Wor]+Attributes[Dec])/5)*0.8)+(((Attributes[Cro]+Attributes[Fir]+Attributes[OtB]+Attributes[Tec]+Attributes[Ant]+Attributes[Cmp]+Attributes[Sta]+Attributes[Vis])/8)*0.2))+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4)*0.1)

Wide Mid Su = ((((Attributes[Pas]+Attributes[Tck]+Attributes[Tea]+Attributes[Wor]+Attributes[Dec])/5)*0.8)+(((Attributes[Cro]+Attributes[Fir]+Attributes[OtB]+Attributes[Tec]+Attributes[Ant]+Attributes[Cmp]+Attributes[Sta]+Attributes[Pos]+Attributes[Vis]+Attributes[Cnt])/10)*0.2))+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4)*0.1)

Wide Mid De = ((((Attributes[Pas]+Attributes[Tck]+Attributes[Pos]+Attributes[Tea]+Attributes[Wor]+Attributes[Cnt]+Attributes[Dec])/7)*0.8)+(((Attributes[Cro]+Attributes[Fir]+Attributes[Mar]+Attributes[Tec]+Attributes[Ant]+Attributes[Cmp]+Attributes[Sta])/7)*0.2))+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4)*0.1)

Def Wing Su = ((((Attributes[Tec]+Attributes[OtB]+Attributes[Pos]+Attributes[Tea]+Attributes[Wor]+Attributes[Sta])/6)*0.8)+(((Attributes[Cro]+Attributes[Dri]+Attributes[Fir]+Attributes[Mar]+Attributes[Tck]+Attributes[Agg]+Attributes[Cnt]+Attributes[Dec]+Attributes[Acc]+Attributes[Cmp]+Attributes[Pas])/11)*0.2))+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4)*0.1)

Def Wing De = ((((Attributes[Tec]+Attributes[OtB]+Attributes[Pos]+Attributes[Tea]+Attributes[Wor]+Attributes[Sta])/6)*0.8)+(((Attributes[Cro]+Attributes[Dri]+Attributes[Fir]+Attributes[Mar]+Attributes[Tck]+Attributes[Agg]+Attributes[Cnt]+Attributes[Dec]+Attributes[Acc])/9)*0.2))+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4)*0.1)

Inv Wing At = ((((Attributes[Cro]+Attributes[Dri]+Attributes[Pas]+Attributes[Tec]+Attributes[Acc]+Attributes[Agi])/6)*0.8)+(((Attributes[Fir]+Attributes[Lon]+Attributes[OtB]+Attributes[Wor]+Attributes[Bal]+Attributes[Pac]+Attributes[Sta]+Attributes[Vis]+Attributes[Cmp]+Attributes[Dec]+Attributes[Ant]+Attributes[Fla])/12)*0.2))+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4)*0.1)

Inv Wing Su = ((((Attributes[Cro]+Attributes[Dri]+Attributes[Pas]+Attributes[Tec]+Attributes[Acc]+Attributes[Agi])/6)*0.8)+(((Attributes[Fir]+Attributes[Lon]+Attributes[OtB]+Attributes[Wor]+Attributes[Bal]+Attributes[Pac]+Attributes[Sta]+Attributes[Vis]+Attributes[Cmp]+Attributes[Dec])/10)*0.2))+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4)*0.1)

Winger Su = ((((Attributes[Cro]+Attributes[Dri]+Attributes[Tec]+Attributes[Acc]+Attributes[Agi])/5)*0.8)+(((Attributes[Fir]+Attributes[Pas]+Attributes[OtB]+Attributes[Wor]+Attributes[Bal]+Attributes[Pac]+Attributes[Sta])/7)*0.2))+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4)*0.1)

Winger At = ((((Attributes[Cro]+Attributes[Dri]+Attributes[Tec]+Attributes[Acc]+Attributes[Agi])/5)*0.8)+(((Attributes[Fir]+Attributes[Pas]+Attributes[OtB]+Attributes[Wor]+Attributes[Bal]+Attributes[Pac]+Attributes[Sta]+Attributes[Fla]+Attributes[Ant])/8)*0.2))+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4)*0.1)

Tq At = ((((Attributes[Dri]+Attributes[Fir]+Attributes[Pas]+Attributes[Tec]+Attributes[Cmp]+Attributes[Dec]+Attributes[Fla]+Attributes[OtB]+Attributes[Vis]+Attributes[Acc])/10)*0.8)+(((Attributes[Fin]+Attributes[Ant]+Attributes[Agi]+Attributes[Bal])/4)*0.2))+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4)*0.1)

Eng Su = ((((Attributes[Fir]+Attributes[Pas]+Attributes[Tec]+Attributes[Cmp]+Attributes[Dec]+Attributes[Vis])/6)*0.8)+(((Attributes[Dri]+Attributes[Ant]+Attributes[Fla]+Attributes[OtB]+Attributes[Tea]+Attributes[Agi])/6)*0.2))+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4)*0.1)

AMC At = ((((Attributes[Fir]+Attributes[Lon]+Attributes[Pas]+Attributes[Tec]+Attributes[Ant]+Attributes[Dec]+Attributes[Fla]+Attributes[OtB])/8)*0.8)+(((Attributes[Dri]+Attributes[Cmp]+Attributes[Vis]+Attributes[Agi]+Attributes[Fin])/5)*0.2))+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4)*0.1)

AMC Su = ((((Attributes[Fir]+Attributes[Lon]+Attributes[Pas]+Attributes[Tec]+Attributes[Ant]+Attributes[Dec]+Attributes[Fla]+Attributes[OtB])/8)*0.8)+(((Attributes[Dri]+Attributes[Cmp]+Attributes[Vis]+Attributes[Agi])/4)*0.2))+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4)*0.1)

SS At = ((((Attributes[Dri]+Attributes[Fin]+Attributes[Fir]+Attributes[Ant]+Attributes[Cmp]+Attributes[OtB]+Attributes[Acc])/7)*0.8)+(((Attributes[Pas]+Attributes[Tec]+Attributes[Cnt]+Attributes[Dec]+Attributes[Wor]+Attributes[Agi]+Attributes[Bal]+Attributes[Pac]+Attributes[Sta])/9)*0.2))+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4)*0.1)

AP At = ((((Attributes[Fir]+Attributes[Pas]+Attributes[Tec]+Attributes[Cmp]+Attributes[Dec]+Attributes[OtB]+Attributes[Tea]+Attributes[Vis])/8)*0.8)+(((Attributes[Dri]+Attributes[Ant]+Attributes[Fla]+Attributes[Agi]+Attributes[Acc])/5)*0.2))+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4)*0.1)

AP Su = ((((Attributes[Fir]+Attributes[Pas]+Attributes[Tec]+Attributes[Cmp]+Attributes[Dec]+Attributes[OtB]+Attributes[Tea]+Attributes[Vis])/8)*0.8)+(((Attributes[Dri]+Attributes[Ant]+Attributes[Fla]+Attributes[Agi])/4)*0.2))+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4)*0.1)

Car Su = ((((Attributes[Fir]+Attributes[Pas]+Attributes[Tck]+Attributes[Dec]+Attributes[Pos]+Attributes[Tea]+Attributes[Sta])/7)*0.8)+(((Attributes[Tec]+Attributes[Cmp]+Attributes[Ant]+Attributes[Cnt]+Attributes[OtB]+Attributes[Vis]+Attributes[Wor])/7)*0.2))+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4)*0.1)

B2B Su = ((((Attributes[Pas]+Attributes[Tck]+Attributes[OtB]+Attributes[Tea]+Attributes[Wor]+Attributes[Sta])/6)*0.8)+(((Attributes[Dri]+Attributes[Fin]+Attributes[Fir]+Attributes[Lon]+Attributes[Tec]+Attributes[Agg]+Attributes[Ant]+Attributes[Cmp]+Attributes[Dec]+Attributes[Pos]+Attributes[Acc]+Attributes[Bal]+Attributes[Pac]+Attributes[Str])/14)*0.2))+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4)*0.1)

Mez At = ((((Attributes[Pas]+Attributes[Tec]+Attributes[Wor]+Attributes[OtB]+Attributes[Dec]+Attributes[Acc])/6)*0.8)+(((Attributes[Dri]+Attributes[Fir]+Attributes[Lon]+Attributes[Fin]+Attributes[Ant]+Attributes[Cmp]+Attributes[Vis]+Attributes[Bal]+Attributes[Sta]+Attributes[Fla])/10)*0.2))+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4)*0.1)

Mez Su = ((((Attributes[Pas]+Attributes[Tec]+Attributes[Wor]+Attributes[OtB]+Attributes[Dec]+Attributes[Acc])/6)*0.8)+(((Attributes[Dri]+Attributes[Fir]+Attributes[Lon]+Attributes[Tck]+Attributes[Ant]+Attributes[Cmp]+Attributes[Vis]+Attributes[Bal]+Attributes[Sta])/9)*0.2))+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4)*0.1)

CM At = ((((Attributes[Fir]+Attributes[Pas]+Attributes[Tck]+Attributes[Dec]+Attributes[Tea])/5)*0.8)+(((Attributes[Tec]+Attributes[Ant]+Attributes[Cmp]+Attributes[Lon]+Attributes[OtB]+Attributes[Vis]+Attributes[Wor]+Attributes[Sta]+Attributes[Acc])/9)*0.2))+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4)*0.1)

CM Su = ((((Attributes[Fir]+Attributes[Pas]+Attributes[Tck]+Attributes[Dec]+Attributes[Tea])/5)*0.8)+(((Attributes[Tec]+Attributes[Ant]+Attributes[Cmp]+Attributes[Cnt]+Attributes[OtB]+Attributes[Vis]+Attributes[Wor]+Attributes[Sta])/8)*0.2))+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4)*0.1)

CM De = ((((Attributes[Tck]+Attributes[Cnt]+Attributes[Dec]+Attributes[Pos]+Attributes[Tea])/5)*0.8)+(((Attributes[Fir]+Attributes[Mar]+Attributes[Pas]+Attributes[Tec]+Attributes[Agg]+Attributes[Ant]+Attributes[Cmp]+Attributes[Wor]+Attributes[Sta])/9)*0.2))+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4)*0.1)

RPM Su = ((((Attributes[Fir]+Attributes[Pas]+Attributes[Tec]+Attributes[OtB]+Attributes[Dec]+Attributes[Cmp]+Attributes[Ant]+Attributes[Tea]+Attributes[Vis]+Attributes[Wor]+Attributes[Acc]+Attributes[Sta])/12)*0.8)+(((Attributes[Dri]+Attributes[Lon]+Attributes[Pos]+Attributes[Cnt]+Attributes[Agi]+Attributes[Bal]+Attributes[Pac])/7)*0.2))+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4)*0.1)

Half Back = ((((Attributes[Mar]+Attributes[Tck]+Attributes[Ant]+Attributes[Cmp]+Attributes[Cnt]+Attributes[Dec]+Attributes[Pos]+Attributes[Tea])/8)*0.8)+(((Attributes[Fir]+Attributes[Pas]+Attributes[Agg]+Attributes[Bra]+Attributes[Wor]+Attributes[Jum]+Attributes[Sta]+Attributes[Str])/8)*0.2))+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4)*0.1)

Reg = ((((Attributes[Fir]+Attributes[Pas]+Attributes[Tec]+Attributes[Cmp]+Attributes[Dec]+Attributes[Fla]+Attributes[OtB]+Attributes[Tea]+Attributes[Vis])/9)*0.8)+(((Attributes[Dri]+Attributes[Lon]+Attributes[Ant]+Attributes[Bal])/4)*0.2))+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4)*0.1)

Anc = ((((Attributes[Mar]+Attributes[Tck]+Attributes[Ant]+Attributes[Cnt]+Attributes[Dec]+Attributes[Pos])/6)*0.8)+(((Attributes[Cmp]+Attributes[Tea]+Attributes[Str])/3)*0.2))+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4)*0.1)

DLP Su = ((((Attributes[Fir]+Attributes[Pas]+Attributes[Tec]+Attributes[Cmp]+Attributes[Dec]+Attributes[Tea]+Attributes[Vis])/7)*0.8)+(((Attributes[OtB]+Attributes[Ant]+Attributes[Pos]+Attributes[Bal])/4)*0.2))+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4)*0.1)

DLP De = ((((Attributes[Fir]+Attributes[Pas]+Attributes[Tec]+Attributes[Cmp]+Attributes[Dec]+Attributes[Tea]+Attributes[Vis])/7)*0.8)+(((Attributes[Tck]+Attributes[Ant]+Attributes[Pos]+Attributes[Bal])/4)*0.2))+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4)*0.1)

SV Su = ((((Attributes[Mar]+Attributes[Pas]+Attributes[Tck]+Attributes[OtB]+Attributes[Pos]+Attributes[Wor]+Attributes[Pac]+Attributes[Sta])/8)*0.8)+(((Attributes[Fin]+Attributes[Fir]+Attributes[Lon]+Attributes[Ant]+Attributes[Cmp]+Attributes[Cnt]+Attributes[Dec]+Attributes[Acc]+Attributes[Bal]+Attributes[Str])/10)*0.2))+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4)*0.1)

DM S = (((Attributes[Tck]+Attributes[Ant]+Attributes[Tea]+Attributes[Cnt])/4)*0.8)+(((Attributes[Mar]+Attributes[Pas]+Attributes[Cmp]+Attributes[Dec]+Attributes[Agg]+Attributes[Wor]+Attributes[Str]+Attributes[Sta]+Attributes[Fir])/9)*0.2)+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4)*0.1)

DM D = (((Attributes[Tck]+Attributes[Ant]+Attributes[Tea]+Attributes[Cnt])/4)*0.8)+(((Attributes[Mar]+Attributes[Pas]+Attributes[Cmp]+Attributes[Dec]+Attributes[Agg]+Attributes[Wor]+Attributes[Str]+Attributes[Sta])/8)*0.2)+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4)*0.1)

BWM Su = (((Attributes[Tck]+Attributes[Agg]+Attributes[Ant]+Attributes[Tea]+Attributes[Wor]+Attributes[Sta])/6)*0.8)+(((Attributes[Mar]+Attributes[Bra]+Attributes[Cnt]+Attributes[Pas]+Attributes[Agi]+Attributes[Pac]+Attributes[Str])/7)*0.2)+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4)*0.1)

BWM De = (((Attributes[Tck]+Attributes[Agg]+Attributes[Ant]+Attributes[Tea]+Attributes[Wor]+Attributes[Sta])/6)*0.8)+(((Attributes[Mar]+Attributes[Bra]+Attributes[Cnt]+Attributes[Pos]+Attributes[Agi]+Attributes[Pac]+Attributes[Str])/7)*0.2)+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4)*0.1)

CWB At = (((Attributes[Cro]+Attributes[Dri]+Attributes[Tec]+Attributes[Wor]+Attributes[Tea]+Attributes[OtB]+Attributes[Sta]+Attributes[Acc])/8)*0.8)+(((Attributes[Fir]+Attributes[Mar]+Attributes[Pas]+Attributes[Tck]+Attributes[Ant]+Attributes[Dec]+Attributes[Fla]+Attributes[Pos]+Attributes[Agi]+Attributes[Bal]+Attributes[Pac])/11)*0.2)+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4)*0.1)

CWB Su = (((Attributes[Cro]+Attributes[Dri]+Attributes[Tec]+Attributes[Wor]+Attributes[Tea]+Attributes[OtB]+Attributes[Sta]+Attributes[Acc])/8)*0.8)+(((Attributes[Fir]+Attributes[Mar]+Attributes[Pas]+Attributes[Tck]+Attributes[Ant]+Attributes[Dec]+Attributes[Fla]+Attributes[Pos]+Attributes[Agi]+Attributes[Bal]+Attributes[Pac])/11)*0.2)+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4)*0.1)

IWB At = (((Attributes[Pas]+Attributes[Tck]+Attributes[Pos]+Attributes[Tea]+Attributes[Ant]+Attributes[Dec])/6)*0.8)+(((Attributes[Fir]+Attributes[Mar]+Attributes[Tec]+Attributes[Cmp]+Attributes[Cnt]+Attributes[OtB]+Attributes[Wor]+Attributes[Agi]+Attributes[Acc]+Attributes[Sta]+Attributes[Vis]+Attributes[Pac]+Attributes[Dri]+Attributes[Cro]+Attributes[Lon]+Attributes[Fla])/16)*0.2)+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4*0.1))

IWB Su = (((Attributes[Pas]+Attributes[Tck]+Attributes[Pos]+Attributes[Tea]+Attributes[Ant]+Attributes[Dec])/6)*0.8)+(((Attributes[Fir]+Attributes[Mar]+Attributes[Tec]+Attributes[Cmp]+Attributes[Cnt]+Attributes[OtB]+Attributes[Wor]+Attributes[Agi]+Attributes[Acc]+Attributes[Sta]+Attributes[Vis])/11)*0.2)+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4*0.1))

IWB De = (((Attributes[Pas]+Attributes[Tck]+Attributes[Pos]+Attributes[Tea]+Attributes[Ant]+Attributes[Dec])/6)*0.8)+(((Attributes[Fir]+Attributes[Mar]+Attributes[Tec]+Attributes[Cmp]+Attributes[Cnt]+Attributes[OtB]+Attributes[Wor]+Attributes[Agi]+Attributes[Acc]+Attributes[Sta])/10)*0.2)+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4*0.1))

IFB De = (((Attributes[Hea]+Attributes[Mar]+Attributes[Tck]+Attributes[Pos]+Attributes[Str])/5)*0.8)+(((Attributes[Dri]+Attributes[Fir]+Attributes[Pas]+Attributes[Tec]+Attributes[Agg]+Attributes[Ant]+Attributes[Bra]+Attributes[Cmp]+Attributes[Cnt]+Attributes[Dec]+Attributes[Wor]+Attributes[Agi]+Attributes[Jum]+Attributes[Pac])/14)*0.2)+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4*0.1))

WB At = (((Attributes[Cro]+Attributes[Dri]+Attributes[Mar]+Attributes[Tck]+Attributes[OtB]+Attributes[Tea]+Attributes[Wor]+Attributes[Sta]+Attributes[Acc])/9)*0.8)+(((Attributes[Fir]+Attributes[Pas]+Attributes[Tec]+Attributes[Dec]+Attributes[Cnt]+Attributes[Agi]+Attributes[Bal]+Attributes[Pac]+Attributes[Ant]+Attributes[Fla])/10)*0.2)+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4*0.1))

WB Su = (((Attributes[Cro]+Attributes[Dri]+Attributes[Mar]+Attributes[Tck]+Attributes[Tea]+Attributes[Wor]+Attributes[Sta]+Attributes[Acc]+Attributes[OtB])/9)*0.8)+(((Attributes[Fir]+Attributes[Pas]+Attributes[Tec]+Attributes[Dec]+Attributes[Cnt]+Attributes[Agi]+Attributes[Bal]+Attributes[Pac]+Attributes[Ant])/9)*0.2)+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4*0.1))

WB De = (((Attributes[Mar]+Attributes[Tck]+Attributes[Pos]+Attributes[Tea]+Attributes[Wor]+Attributes[Ant]+Attributes[Sta]+Attributes[Acc])/8)*0.8)+(((Attributes[Cro]+Attributes[Dri]+Attributes[Fir]+Attributes[Pas]+Attributes[Tec]+Attributes[Dec]+Attributes[Cnt]+Attributes[OtB]+Attributes[Agi]+Attributes[Bal]+Attributes[Pac])/11)*0.2)+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4*0.1))

FB At = (((Attributes[Mar]+Attributes[Tck]+Attributes[Cro]+Attributes[Pos]+Attributes[Ant]+Attributes[Tea])/6)*0.8)+(((Attributes[Dri]+Attributes[Fir]+Attributes[Pas]+Attributes[Tec]+Attributes[Wor]+Attributes[Dec]+Attributes[Cnt]+Attributes[OtB]+Attributes[Agi]+Attributes[Sta]+Attributes[Pac])/11)*0.2)+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4*0.1))

FB Su = (((Attributes[Mar]+Attributes[Tck]+Attributes[Tea]+Attributes[Pos]+Attributes[Cnt]+Attributes[Ant])/6)*0.8)+(((Attributes[Cro]+Attributes[Dri]+Attributes[Pas]+Attributes[Tec]+Attributes[Wor]+Attributes[Dec]+Attributes[Sta]+Attributes[Pac])/8)*0.2)+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4*0.1))

FB De = (((Attributes[Mar]+Attributes[Tck]+Attributes[Pos]+Attributes[Cnt]+Attributes[Ant])/5)*0.8)+(((Attributes[Cro]+Attributes[Pas]+Attributes[Tea]+Attributes[Wor]+Attributes[Dec]+Attributes[Sta]+Attributes[Pac])/7)*0.2)+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4*0.1))

Lib Su = (((Attributes[Fir]+Attributes[Hea]+Attributes[Mar]+Attributes[Pas]+Attributes[Tck]+Attributes[Tec]+Attributes[Dec]+Attributes[Cmp]+Attributes[Pos]+Attributes[Tea]+Attributes[Str]+Attributes[Jum])/12)*0.8)+(((Attributes[Ant]+Attributes[Bra]+Attributes[Cnt]+Attributes[Pac]+Attributes[Sta]+Attributes[Dri]+Attributes[Vis])/7)*0.2)+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4*0.1))

Lib De = (((Attributes[Fir]+Attributes[Hea]+Attributes[Mar]+Attributes[Pas]+Attributes[Tck]+Attributes[Tec]+Attributes[Dec]+Attributes[Cmp]+Attributes[Pos]+Attributes[Tea]+Attributes[Str]+Attributes[Jum])/12)*0.8)+(((Attributes[Ant]+Attributes[Bra]+Attributes[Cnt]+Attributes[Pac]+Attributes[Sta])/5)*0.2)+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4*0.1))

BPD Co = (((Attributes[Hea]+Attributes[Mar]+Attributes[Pas]+Attributes[Tck]+Attributes[Pos]+Attributes[Cmp]+Attributes[Str]+Attributes[Jum])/8)*0.8)+(((Attributes[Fir]+Attributes[Tec]+Attributes[Pac]+Attributes[Ant]+Attributes[Bra]+Attributes[Cnt]+Attributes[Dec]+Attributes[Vis])/8)*0.2)+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4*0.1))

BPD St = (((Attributes[Hea]+Attributes[Mar]+Attributes[Pas]+Attributes[Tck]+Attributes[Pos]+Attributes[Cmp]+Attributes[Str]+Attributes[Jum])/8)*0.8)+(((Attributes[Fir]+Attributes[Tec]+Attributes[Agg]+Attributes[Ant]+Attributes[Bra]+Attributes[Cnt]+Attributes[Dec]+Attributes[Vis])/8)*0.2)+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4*0.1))

BPD De = (((Attributes[Hea]+Attributes[Mar]+Attributes[Pas]+Attributes[Tck]+Attributes[Pos]+Attributes[Cmp]+Attributes[Str]+Attributes[Jum])/8)*0.8)+(((Attributes[Fir]+Attributes[Tec]+Attributes[Agg]+Attributes[Ant]+Attributes[Bra]+Attributes[Cnt]+Attributes[Dec]+Attributes[Vis]+Attributes[Pac])/9)*0.2)+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4*0.1))

WCB At = (((Attributes[Dri]+Attributes[Hea]+Attributes[Mar]+Attributes[Tck]+Attributes[Pos]+Attributes[Pac]+Attributes[Str]+Attributes[Jum]+Attributes[Sta])/9)*0.8)+(((Attributes[Cro]+Attributes[Fir]+Attributes[Pas]+Attributes[Tec]+Attributes[Agg]+Attributes[Ant]+Attributes[Bra]+Attributes[Cmp]+Attributes[Cnt]+Attributes[Dec]+Attributes[OtB]+Attributes[Wor]+Attributes[Agi])/13)*0.2)+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4*0.1))

WCB Su = (((Attributes[Dri]+Attributes[Hea]+Attributes[Mar]+Attributes[Tck]+Attributes[Pos]+Attributes[Pac]+Attributes[Str]+Attributes[Jum])/8)*0.8)+(((Attributes[Cro]+Attributes[Fir]+Attributes[Pas]+Attributes[Tec]+Attributes[Agg]+Attributes[Ant]+Attributes[Bra]+Attributes[Cmp]+Attributes[Cnt]+Attributes[Dec]+Attributes[OtB]+Attributes[Wor]+Attributes[Agi]+Attributes[Sta])/14)*0.2)+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4*0.1))

WCB De = (((Attributes[Hea]+Attributes[Mar]+Attributes[Tck]+Attributes[Pos]+Attributes[Str]+Attributes[Jum])/6)*0.8)+(((Attributes[Dri]+Attributes[Fir]+Attributes[Pas]+Attributes[Tec]+Attributes[Agg]+Attributes[Ant]+Attributes[Bra]+Attributes[Cmp]+Attributes[Cnt]+Attributes[Dec]+Attributes[Wor]+Attributes[Agi]+Attributes[Pac])/13)*0.2)+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4*0.1))

CB Co = (((Attributes[Tck]+Attributes[Pos]+Attributes[Dec]+Attributes[Cnt]+Attributes[Ant]+Attributes[Pac])/6)*0.8)+(((Attributes[Cmp]+Attributes[Hea]+Attributes[Bra]+Attributes[Str]+Attributes[Jum])/5)*0.2)+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4*0.1))

CB St = (((Attributes[Hea]+Attributes[Tck]+Attributes[Dec]+Attributes[Pos]+Attributes[Str]+Attributes[Jum]+Attributes[Bra]+Attributes[Agg])/8)*0.8)+(((Attributes[Cnt]+Attributes[Ant]+Attributes[Cmp]+Attributes[Mar])/4)*0.2)+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4*0.1))

CB D = (((Attributes[Hea]+Attributes[Tck]+Attributes[Mar]+Attributes[Pos]+Attributes[Str]+Attributes[Jum])/6)*0.8)+(((Attributes[Cnt]+Attributes[Pac]+Attributes[Agg]+Attributes[Ant]+Attributes[Bra]+Attributes[Cmp]+Attributes[Dec])/7)*0.2)+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4*0.1))

NCB Co = (((Attributes[Hea]+Attributes[Tck]+Attributes[Ant]+Attributes[Bra]+Attributes[Pos]+Attributes[Str]+Attributes[Jum])/7)*0.8)+(((Attributes[Mar]+Attributes[Cnt]+Attributes[Pac])/3)*0.2)+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4*0.1))

NCB De = (((Attributes[Hea]+Attributes[Tck]+Attributes[Agg]+Attributes[Bra]+Attributes[Pos]+Attributes[Str]+Attributes[Jum])/7)*0.8)+(((Attributes[Mar]+Attributes[Cnt]+Attributes[Ant]+Attributes[Pac])/4)*0.2)+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4*0.1))

NCB St = (((Attributes[Hea]+Attributes[Tck]+Attributes[Agg]+Attributes[Bra]+Attributes[Pos]+Attributes[Str]+Attributes[Jum])/7)*0.8)+(((Attributes[Mar]+Attributes[Cnt]+Attributes[Ant])/3)*0.2)+(((Attributes[Acc]+Attributes[Jum]+Attributes[Pac]+Attributes[Det])/4*0.1))

    """

    pattern = re.compile(r"(?P<role>[A-Za-z0-9\s]+)=\s*(?P<formula>\(+.*)")
    formulas = {}
    for line in formula_text.splitlines():
        match = pattern.match(line.strip())
        if match:
            role = match.group("role").strip()
            formula = match.group("formula").strip()
            formulas[role] = formula

    # Evaluate formula for each player
    def evaluate_formula(formula: str, player: dict) -> float:
        eval_formula = formula
        for attr in re.findall(r"Attributes\[(\w+)\]", formula):
            value = player.get(attr, 0)
            eval_formula = eval_formula.replace(f"Attributes[{attr}]", str(value))
        try:
            return round(eval(eval_formula), 2)
        except:
            return None

    players_data = {
        row["Name"]: row.to_dict()
        for _, row in attributes_df.iterrows()
    }

    results = []
    for player_name, player_data in players_data.items():
        for role, formula in formulas.items():
            score = evaluate_formula(formula, player_data)
            if score is not None:
                results.append({"Player": player_name, "Role": role, "Score": score})

    results_df = pd.DataFrame(results)
    
    # Add ranking per role (1 = best score)
    results_df["Rank"] = results_df.groupby("Role")["Score"].rank(ascending=False, method="min")

    st.success("Role scores calculated!")

    # Get top player per role
    top_players = results_df.loc[results_df.groupby("Role")["Score"].idxmax()].reset_index(drop=True)

    with st.expander("🏆 View Top Player Per Role", expanded=False):
        st.dataframe(top_players.sort_values(by="Role"), use_container_width=True)

    # Show top roles per player
    with st.expander("🔍 View Ranked Role Scores Per Player", expanded=True):
        player_list = results_df["Player"].unique().tolist()
        selected_player = st.selectbox("Select a player to view their roles:", player_list)
        player_roles = results_df[results_df["Player"] == selected_player].sort_values(by="Score", ascending=False)
        st.dataframe(player_roles, use_container_width=True)

   
    
    # All scores table
    with st.expander("📋 View All Role Scores Table"):
        pivot_df = results_df.pivot(index="Player", columns="Role", values="Score")

        if pivot_df.empty:
            st.warning("No role scores available to display.")
        else:
        # Value range filter
            min_score = float(pivot_df.min().min())
            max_score = float(pivot_df.max().max())

        # Defensive check to avoid slider errors
            if min_score == max_score:
                 st.info(f"All scores are the same: {min_score:.2f}")
                 score_range = (min_score, max_score)
            else:
                score_range = st.slider(
                "Select score range to filter players",
                min_value=round(min_score, 2),
                max_value=round(max_score, 2),
                value=(round(min_score, 2), round(max_score, 2)),
                step=0.01
            )

        # Apply filter
        mask = pivot_df.apply(lambda row: row.between(score_range[0], score_range[1]).any(), axis=1)
        filtered_df = pivot_df[mask]

    # Apply filter: keep rows where any score is within the selected range
    mask = pivot_df.apply(lambda row: row.between(score_range[0], score_range[1]).any(), axis=1)
    filtered_df = pivot_df[mask]

    role_groups = {
        # Defensive
        "BPD Co": "Defensive", "BPD De": "Defensive", "BPD St": "Defensive",
        "CB Co": "Defensive", "CB D": "Defensive", "CB St": "Defensive", 
        "NCB St": "Defensive", "NCB Co": "Defensive", "NCB De": "Defensive",
        "WCB At": "Defensive", "WCB De": "Defensive", "WCB Su": "Defensive",
        "Lib Su": "Defensive", "Lib De": "Defensive",
        "FB De": "Defensive", "FB Su": "Defensive", "FB At": "Defensive",
        "IFB De": "Defensive", "IWB De": "Defensive", "IWB Su": "Defensive", "IWB At": "Defensive",
        "WB De": "Defensive", "WB Su": "Defensive", "WB At": "Defensive",

        # Midfield
        "BWM De": "Midfield", "BWM Su": "Midfield", "DM D": "Midfield", "DM S": "Midfield",
        "DLP De": "Midfield", "DLP Su": "Midfield", "Half Back": "Midfield", "Anc": "Midfield",
        "SV Su": "Midfield", "RPM Su": "Midfield", "Reg": "Midfield",
        "CM De": "Midfield", "CM Su": "Midfield", "CM At": "Midfield",
        "B2B Su": "Midfield", "AP Su": "Midfield", "AP At": "Midfield",
        "Def Wing De": "Midfield", "Def Wing Su": "Midfield",
        "Wide Mid De": "Midfield", "Wide Mid Su": "Midfield", "Wide Mid At": "Midfield",
        "Mez Su": "Midfield", "Mez At": "Midfield",
        "Winger Su": "Midfield", "Winger At": "Midfield",
        "AMC Su": "Midfield", "AMC At": "Midfield",
        "Inv Wing Su": "Midfield", "Inv Wing At": "Midfield",

        # Attacking
        "IF A": "Attacking", "IF S": "Attacking", "Eng Su": "Attacking",
        "Tq At": "Attacking", "TF Su": "Attacking", "TF At": "Attacking",
        "SS At": "Attacking", "Pre Fwd De": "Attacking", "Pre Fwd Su": "Attacking", "Pre Fwd At": "Attacking",
        "Poach At": "Attacking", "F9 Su": "Attacking",
        "CF Su": "Attacking", "CF At": "Attacking",
        "AF At": "Attacking"
    }

    group_order = ["Defensive", "Midfield", "Attacking"]
    ordered_roles = sorted(filtered_df.columns, key=lambda role: (group_order.index(role_groups.get(role, "Midfield")), role))
    filtered_df = filtered_df[ordered_roles]

    def highlight_max(s):
        is_max = s == s.max()
        return ['background-color: #006400; color: white' if v else '' for v in is_max]

    styled_filtered_df = (
        filtered_df.style
        .apply(highlight_max, axis=1)
        .format("{:.2f}")
    )

    st.dataframe(styled_filtered_df, use_container_width=True)

    with st.expander("🎯 Show Players Outside Top N in Every Role", expanded=False):
        rank_threshold = st.selectbox("Only show players ranked *outside* top N across all roles:", [5, 10, 12], index=1)
        display_option = st.radio("View:", ["Scores", "Ranks"], horizontal=True)

    # Create pivot tables
        score_pivot = results_df.pivot(index="Player", columns="Role", values="Score")
        rank_pivot = results_df.pivot(index="Player", columns="Role", values="Rank")

    # Filter: player must be ranked *worse than* N in all roles
        mask_outside_top_n = rank_pivot.apply(lambda row: row.dropna().min() > rank_threshold, axis=1)
        outside_top_n_players = rank_pivot[mask_outside_top_n]

    if outside_top_n_players.empty:
        st.warning(f"All players have at least one role ranked within top {rank_threshold}.")
    else:
        if display_option == "Scores":
            df_to_display = score_pivot.loc[outside_top_n_players.index]
            st.dataframe(df_to_display.style.format("{:.2f}"), use_container_width=True)
        else:
            df_to_display = rank_pivot.loc[outside_top_n_players.index]
            st.dataframe(df_to_display.style.format("{:.0f}"), use_container_width=True)
else:
    st.info("Please upload a file to begin.")
