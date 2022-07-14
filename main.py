import requests
import json
import time
import threading as th

development_api_key = "RGAPI-66df8167-a304-4cde-a5c4-17d3a55dc37b"
persist = True


def key_capture_thread():
    global persist
    input()
    persist = False


def query_summoner_info_by_summoner_name_response(summoner_name):
    query = (f"https://na1.api.riotgames.com/tft/summoner/v1/"
             f"summoners/by-name/{summoner_name}?"
             f"api_key={development_api_key}")
    response = requests.get(query)
    return response


def query_ladder_info_by_summoner_name_response(summoner_name):
    summoner_id = get_summoner_id_from_summoner_name(summoner_name)
    query = (f"https://na1.api.riotgames.com/tft/league/v1/"
             f"entries/by-summoner/{summoner_id}?"
             f"api_key={development_api_key}")
    response = requests.get(query)
    return response


def query_matches_by_summoner_name_response(summoner_name, start_index=0, num_matches=20):
    puuid = get_puuid_from_summoner_name(summoner_name)
    query = (f"https://americas.api.riotgames.com/tft/match/v1/"
             f"matches/by-puuid/{puuid}/ids?"
             f"start={start_index}&"
             f"count={num_matches}&"
             f"api_key={development_api_key}")
    response = requests.get(query)
    return response


def query_matches_by_summoner_name_list(summoner_name, start_index=0, num_matches=20):
    puuid = get_puuid_from_summoner_name(summoner_name)
    query = (f"https://americas.api.riotgames.com/tft/match/v1/"
             f"matches/by-puuid/{puuid}/ids?"
             f"start={start_index}&"
             f"count={num_matches}&"
             f"api_key={development_api_key}")
    response = requests.get(query)
    return list(response.json())


def query_match_by_match_id_response(match_id):
    query = (f"https://americas.api.riotgames.com/tft/match/v1/"
             f"matches/{match_id}?"
             f"api_key={development_api_key}")
    response = requests.get(query)
    return response


def get_puuid_from_summoner_name(summoner_name):
    response = query_summoner_info_by_summoner_name_response(summoner_name)
    puuid = response.json().get("puuid")
    return puuid


def get_summoner_id_from_summoner_name(summoner_name):
    response = query_summoner_info_by_summoner_name_response(summoner_name)
    summoner_id = response.json().get("id")
    return summoner_id


def get_last_match_id_from_summoner_name(summoner_name):
    return get_nth_match_id_from_summoner_name(summoner_name, 1)


def get_nth_match_id_from_summoner_name(summoner_name, n):
    return query_matches_by_summoner_name_list(summoner_name, num_matches=n)[-1]


def get_match_json_from_match_id(match_id):
    return query_match_by_match_id_response(match_id).json()


def print_response_status_code(response):
    print(f"STATUS CODE: {response.status_code}\n")


def print_response_body(response):
    print(f"RESPONSE BODY: {json.dumps(response.json(), sort_keys=False, indent=4)}\n")


def get_game_mode_from_match_json(match):
    game_mode = match["info"]["tft_game_type"]
    match game_mode:
        case "standard":
            return "Standard Ranked"
        case "pairs":
            return "Double-Up"
        case "turbo":
            return "Hyper Roll"
        case _:
            return "ERROR: Game Type Unknown"


def get_summoner_index_in_match_from_match_json(summoner_name, match):
    return match["metadata"]["participants"].index(get_puuid_from_summoner_name(summoner_name))


def get_summoner_placement_in_match_json_from_summoner_name(summoner_name, match):
    placement = match["info"]["participants"][get_summoner_index_in_match_from_match_json(summoner_name, match)][
        "placement"]

    if get_game_mode_from_match_json(match) == "Double-Up":
        match placement:
            case 1:
                return "First"
            case 2:
                return "First"
            case 3:
                return "Second"
            case 4:
                return "Second"
            case 5:
                return "Third"
            case 6:
                return "Third"
            case 7:
                return "Fourth"
            case 8:
                return "Fourth"
            case _:
                return "ERROR: Placement Unknown"
    else:
        match placement:
            case 1:
                return "First"
            case 2:
                return "Second"
            case 3:
                return "Third"
            case 4:
                return "Fourth"
            case 5:
                return "Fifth"
            case 6:
                return "Sixth"
            case 7:
                return "Seventh"
            case 8:
                return "EIF"
            case _:
                return "ERROR: Placement Unknown"


def persistent_status_check(summoner_name):
    th.Thread(target=key_capture_thread, args=(), name='key_capture_thread', daemon=True).start()

    request_interval_seconds = 2.0
    sleep_seconds = 2.0
    current_time = 0

    last_match_id = get_last_match_id_from_summoner_name(summoner_name)
    last_match = get_match_json_from_match_id(last_match_id)
    last_game_mode = get_game_mode_from_match_json(last_match)
    last_placement = get_summoner_placement_in_match_json_from_summoner_name(summoner_name, last_match)

    print(f"Last Match ID: {last_match_id}")
    print(f"Last Game Mode: {last_game_mode}")
    print(f"Last Placement: {last_placement}\n")

    while persist:
        t = time.time()
        if t - current_time >= request_interval_seconds:
            current_match_id = get_nth_match_id_from_summoner_name(summoner_name, 1)
            if current_match_id != last_match_id:
                current_match = get_match_json_from_match_id(current_match_id)
                current_game_mode = get_game_mode_from_match_json(current_match)
                current_placement = (get_summoner_placement_in_match_json_from_summoner_name
                                     (summoner_name, current_match))

                print(f"New Match Found!")
                print(f"Match ID: {current_match_id}")
                print(f"Game Mode: {current_game_mode}")
                print(f"Placement: {current_placement}\n")

                last_match_id = current_match_id
            else:
                print("No new matches found")
            current_time = time.time()
        time.sleep(sleep_seconds)


def main():
    print("STARTING UP TFT BOT...\n")

    # for match_id in query_matches_by_summoner_name_list("SabrinaPleasure", num_matches=1):
    #     print_response_body(query_match_by_match_id_response(match_id))

    # persistent_status_check("Spicy Appies")
    print_response_body(query_match_by_match_id_response(get_nth_match_id_from_summoner_name("DangoWang", 7)))

    print("...SHUTTING DOWN TFT BOT")


if __name__ == '__main__':
    main()
