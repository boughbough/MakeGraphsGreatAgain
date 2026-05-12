import requests


headers = {
    'accept': '*/*',
    'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7,id;q=0.6',
    'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
    'content-type': 'application/json',
    'priority': 'u=1, i',
    'referer': 'https://x.com/realDonaldTrump',
    'sec-ch-ua': '"Not(A:Brand";v="8", "Chromium";v="144", "Opera GX";v="128"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 OPR/128.0.0.0',
    'x-client-transaction-id': 'sGbj6w9sO/JxvyQ2P+llVBZKMWSiJiJSmD5eJ614QjowzwAlYPU7Zjo/q+A/r4m6jDkCybWL0NAfQxILFq2hSD5Cf4X2sw',
    'x-csrf-token': 'ca84bf9993a28b5cdf9d9e44a618e7a14f841874f6c5dd17a673cd83ad774fb7ce62f6f1cb012593313d314a8b95fc4b378e0488c702d11238d7dbc0c68fe500efa2c9e87c58221a97ad68942161f10b',
    'x-twitter-active-user': 'yes',
    'x-twitter-auth-type': 'OAuth2Session',
    'x-twitter-client-language': 'en',
    # 'cookie': 'guest_id=v1%3A176429178454611267; __cuid=7b2a04b6197e4f46a3508c3dab6cf86c; d_prefs=MjoxLGNvbnNlbnRfdmVyc2lvbjoyLHRleHRfdmVyc2lvbjoxMDAw; g_state={"i_l":0,"i_ll":1767799250159}; kdt=5Pu2ElAvfwVsLo1tIXaDgIfKdllc1HnBLZbgIxNp; auth_token=d2d540195ed50895cab55a10b79399a5189a5023; ct0=ca84bf9993a28b5cdf9d9e44a618e7a14f841874f6c5dd17a673cd83ad774fb7ce62f6f1cb012593313d314a8b95fc4b378e0488c702d11238d7dbc0c68fe500efa2c9e87c58221a97ad68942161f10b; twid=u%3D2008921811036291072; lang=en; __cf_bm=dHF7FvG5n2AhYUjnlR_rP9U3V6yt48.6HZcmc9A2DGg-1774785747.771144-1.0.1.1-mhGRFrAPi84Ih5Gn2tbrAMM3zjDBVFG_POd8YE7ZPKHH5w3ZnLOwrc79aRyYEzxzENc9YRo0OLt52MDHFedoG0t.UBQt4qtpBygWjHZaqeFnRTuGncpVgd1efvT.m_3.',
}

params = {
    'variables': '{"userId":"25073877","count":20,"includePromotedContent":true,"withQuickPromoteEligibilityTweetFields":true,"withVoice":true}',
    'features': '{"rweb_video_screen_enabled":false,"profile_label_improvements_pcf_label_in_post_enabled":true,"responsive_web_profile_redirect_enabled":false,"rweb_tipjar_consumption_enabled":false,"verified_phone_label_enabled":false,"creator_subscriptions_tweet_preview_api_enabled":true,"responsive_web_graphql_timeline_navigation_enabled":true,"responsive_web_graphql_skip_user_profile_image_extensions_enabled":false,"premium_content_api_read_enabled":false,"communities_web_enable_tweet_community_results_fetch":true,"c9s_tweet_anatomy_moderator_badge_enabled":true,"responsive_web_grok_analyze_button_fetch_trends_enabled":false,"responsive_web_grok_analyze_post_followups_enabled":true,"responsive_web_jetfuel_frame":true,"responsive_web_grok_share_attachment_enabled":true,"responsive_web_grok_annotations_enabled":true,"articles_preview_enabled":true,"responsive_web_edit_tweet_api_enabled":true,"graphql_is_translatable_rweb_tweet_is_translatable_enabled":true,"view_counts_everywhere_api_enabled":true,"longform_notetweets_consumption_enabled":true,"responsive_web_twitter_article_tweet_consumption_enabled":true,"content_disclosure_indicator_enabled":true,"content_disclosure_ai_generated_indicator_enabled":true,"responsive_web_grok_show_grok_translated_post":false,"responsive_web_grok_analysis_button_from_backend":true,"post_ctas_fetch_enabled":true,"freedom_of_speech_not_reach_fetch_enabled":true,"standardized_nudges_misinfo":true,"tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled":true,"longform_notetweets_rich_text_read_enabled":true,"longform_notetweets_inline_media_enabled":false,"responsive_web_grok_image_annotation_enabled":true,"responsive_web_grok_imagine_annotation_enabled":true,"responsive_web_grok_community_note_auto_translation_is_enabled":false,"responsive_web_enhance_cards_enabled":false}',
    'fieldToggles': '{"withArticlePlainText":false}',
}

response = requests.get(
    'https://x.com/i/api/graphql/FOlovQsiHGDls3c0Q_HaSQ/UserTweets',
    params=params,
    headers=headers,
)