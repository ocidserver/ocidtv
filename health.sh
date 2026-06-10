#!/usr/bin/env bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0"
MAX_JOBS=10
OUTPUT_DIR="./output"
README="./readme.md"

SEPATBOLA_FILE="$OUTPUT_DIR/sepakbola.m3u"
TARUNG_FILE="$OUTPUT_DIR/tarung.m3u"
TV_LOKAL_FILE="$OUTPUT_DIR/tv_lokal.m3u"

for f in "$SEPATBOLA_FILE" "$TARUNG_FILE" "$TV_LOKAL_FILE"; do
    [[ ! -f "$f" ]] && echo "Missing: $f" && exit 1
done

STATUSLOG=$(mktemp)

get_status() {
    local url="$1"
    local channel="$2"
    local category="$3"
    local index="$4"
    local total="$5"
    local response

    [[ "$url" != http* ]] && return

    printf -v chnl_info "%s [%s] (%s)" "$channel" "$category" "$url"

    response=$(
        curl -skL \
            -A "$UA" \
            -H "Accept: */*" \
            -H "Accept-Language: en-US,en;q=0.9" \
            -H "Connection: keep-alive" \
            -o /dev/null \
            --compressed \
            --max-time 10 \
            -w "%{http_code}" \
            "$url" 2>&1
    )

    case "$response" in
        2* | 3*)
            printf '[%d/%d] OK  %s\n' "$((index + 1))" "$total" "$chnl_info"
            echo "PASS|$category" >>"$STATUSLOG"
            ;;
        4* | 5*)
            printf '[%d/%d] FAIL %s\n' "$((index + 1))" "$total" "$chnl_info"
            echo "FAIL|$category|$channel|$response|$url" >>"$STATUSLOG"
            ;;
        *)
            printf '[%d/%d] FAIL %s\n' "$((index + 1))" "$total" "$chnl_info"
            if [[ "$response" == "000" ]]; then
                echo "FAIL|$category|$channel|408|$url" >>"$STATUSLOG"
            else
                echo "FAIL|$category|$channel|$response|$url" >>"$STATUSLOG"
            fi
            ;;
    esac
}

parse_and_check() {
    local file="$1"
    local category="$2"
    local name=""
    local index=0

    while IFS= read -r line; do
        line=$(echo "$line" | tr -d '\r\n')

        if [[ "$line" == \#EXTINF* ]]; then
            name=$(echo "$line" | sed -n 's/.*,\(.*\)$/\1/p')
            [[ -z "$name" ]] && name="Unknown"
        elif [[ "$line" =~ ^https?:// ]]; then
            while (($(jobs -rp | wc -l) >= MAX_JOBS)); do sleep 0.2; done
            get_status "$line" "$name" "$category" "$index" "$total_urls" &
            ((index++))
        fi
    done < "$file"
}

total_urls=$(grep -cE '^https?://' "$SEPATBOLA_FILE" "$TARUNG_FILE" "$TV_LOKAL_FILE" | tail -1 | cut -d: -f2)

printf "Checking %d links across 3 playlists\n" "$total_urls"

echo "category|channel|code|url" >"$STATUSLOG"

parse_and_check "$SEPATBOLA_FILE" "sepakbola"
parse_and_check "$TARUNG_FILE" "tarung"
parse_and_check "$TV_LOKAL_FILE" "tv_lokal"

wait
echo -e "\nDone checking."

write_readme() {
    local passed failed
    passed=$(grep -c '^PASS|' "$STATUSLOG")
    failed=$(grep -c '^FAIL|' "$STATUSLOG")

    local sepakbola_pass sepakbola_fail tarung_pass tarung_fail tvlokal_pass tvlokal_fail
    sepakbola_pass=$(grep -c '^PASS|sepakbola' "$STATUSLOG" || true)
    sepakbola_fail=$(grep -c '^FAIL|sepakbola' "$STATUSLOG" || true)
    tarung_pass=$(grep -c '^PASS|tarung' "$STATUSLOG" || true)
    tarung_fail=$(grep -c '^FAIL|tarung' "$STATUSLOG" || true)
    tvlokal_pass=$(grep -c '^PASS|tv_lokal' "$STATUSLOG" || true)
    tvlokal_fail=$(grep -c '^FAIL|tv_lokal' "$STATUSLOG" || true)

    {
        echo "## Health Check Log @ $(TZ='UTC' date '+%Y-%m-%d %H:%M %Z')"
        echo
        echo "### Overall: Working=$passed | Dead=$failed"
        echo
        echo "| Category | Working | Dead |"
        echo "|----------|---------|------|"
        echo "| Sepakbola | $sepakbola_pass | $sepakbola_fail |"
        echo "| Tarung | $tarung_pass | $tarung_fail |"
        echo "| TV Lokal | $tvlokal_pass | $tvlokal_fail |"
        echo
        if ((failed > 0)); then
            echo "### Dead Streams"
            echo
            grep '^FAIL|' "$STATUSLOG" | while IFS='|' read -r _ cat ch code url; do
                echo "- **$ch** ($cat) - HTTP $code"
            done
            echo
        fi
        echo "---"
        echo "#### Playlist URLs"
        echo
        echo "- Sepakbola: \`output/sepakbola.m3u\`"
        echo "- Tarung: \`output/tarung.m3u\`"
        echo "- TV Lokal: \`output/tv_lokal.m3u\`"
        echo
        echo "---"
        echo "#### Legal Disclaimer"
        echo "This project lists publicly accessible IPTV streams as found on the internet."
        echo "No video or audio content is hosted in this repository."
        echo "These links are provided **solely for educational and research purposes.**"
    } >"$README"
}

write_readme
rm "$STATUSLOG"
echo "README updated."
