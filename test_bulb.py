"""
測試程式：驗證 Mac 能否控制 Tapo 燈泡

這是最簡單的測試程式，用於確認硬體連接是否正常。
如果這一步失敗，後面的主程式也無法運作。
"""

import asyncio
from plugp100.new.device_factory import connect, DeviceConnectConfiguration
from plugp100.new.tapobulb import TapoBulb
from plugp100.new.device_type import DeviceType
from plugp100.common.credentials import AuthCredential

# =============== 請修改這裡 ===============
MY_EMAIL = "kolyfish2@gmail.com"
MY_PASSWORD = "WWuu0921"
MY_IP = "192.168.100.150"  # 例如 "192.168.0.105"
# =========================================


async def main():
    print(f"嘗試連線到 {MY_IP} ...")

    # 建立憑證
    credential = AuthCredential(MY_EMAIL, MY_PASSWORD)

    # 建立連接設定
    config = DeviceConnectConfiguration(
        host=MY_IP,
        port=80,
        credentials=credential,
        device_type=DeviceType.Bulb.value,  # 使用 DeviceType.Bulb.value
    )

    try:
        # 連接燈泡 - 先連接取得 client
        print("正在連接燈泡...")
        device = await connect(config)
        await device.update()
        print("✅ 連接成功！")

        # 檢查可用的 components
        print(f"可用的 components: {[c for c in device.components.as_list()]}")
        
        # 手動建立 TapoBulb 實例（使用已連接的 client）
        bulb = TapoBulb(host=MY_IP, port=80, client=device.client)
        await bulb.update()
        print("✅ TapoBulb 初始化成功！")

        # 1. 開燈
        print("\n💡 開燈！")
        result = await bulb.turn_on()
        result.get_or_raise()  # 如果失敗會拋出異常
        await asyncio.sleep(1)

        # 2. 變綠色 (股市跌/買點)
        print("💚 變綠色！")
        result = await bulb.set_hue_saturation(hue=120, saturation=100)  # Hue 120=Green
        result.get_or_raise()
        result = await bulb.set_brightness(100)
        result.get_or_raise()
        await asyncio.sleep(2)

        # 3. 變紅色 (股市漲/賣點)
        print("❤️ 變紅色！")
        result = await bulb.set_hue_saturation(hue=0, saturation=100)  # Hue 0=Red
        result.get_or_raise()
        result = await bulb.set_brightness(100)
        result.get_or_raise()
        await asyncio.sleep(2)

        # 4. 關燈
        print("\n🌑 測試結束，關燈。")
        result = await bulb.turn_off()
        result.get_or_raise()
        await bulb.client.close()
        print("✅ 硬體測試成功！你可以開始寫主程式了。")

    except Exception as e:
        print(f"\n❌ 發生錯誤：{e}")
        print("\n請檢查：")
        print("1. IP 位址是否正確？")
        print("2. 帳號密碼是否正確？")
        print("3. 燈泡是否有電？")
        print("4. Mac 與燈泡是否在同一個 Wi-Fi 網路？")
        import traceback

        traceback.print_exc()
        try:
            if "bulb" in locals():
                await bulb.client.close()
        except Exception:
            pass


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    finally:
        loop.close()

