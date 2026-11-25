from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.metrics import dp
import json
import os
from datetime import datetime

Window.clearcolor = (0.95, 0.96, 0.98, 1)


class POSApp(App):
    def build(self):
        self.title = "For Sale - POS App"
        self.cart = []
        self.sales_history_file = "sales_history.json"

        root = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(10))

        # Header
        header = BoxLayout(size_hint_y=None, height=dp(50))
        header_lbl = Label(
            text="[b]FOR SALE - POS SYSTEM[/b]",
            markup=True,
            font_size=dp(20),
            color=(0.1, 0.2, 0.4, 1)
        )
        header.add_widget(header_lbl)
        root.add_widget(header)

        # Input Section
        input_grid = GridLayout(cols=2, spacing=dp(8), size_hint_y=None, height=dp(135))

        input_grid.add_widget(Label(text="Item Name:", color=(0.2, 0.2, 0.2, 1), halign="left"))
        self.item_name_input = TextInput(hint_text="e.g. Coffee, Book", multiline=False)
        input_grid.add_widget(self.item_name_input)

        input_grid.add_widget(Label(text="Price (MMK):", color=(0.2, 0.2, 0.2, 1), halign="left"))
        self.price_input = TextInput(hint_text="e.g. 2500", input_filter="float", multiline=False)
        input_grid.add_widget(self.price_input)

        input_grid.add_widget(Label(text="Quantity:", color=(0.2, 0.2, 0.2, 1), halign="left"))
        self.qty_input = TextInput(text="1", input_filter="int", multiline=False)
        input_grid.add_widget(self.qty_input)

        root.add_widget(input_grid)

        # Add Button
        add_btn = Button(
            text="+ Add to Cart",
            size_hint_y=None,
            height=dp(45),
            background_color=(0.13, 0.59, 0.95, 1),
            bold=True
        )
        add_btn.bind(on_press=self.add_to_cart)
        root.add_widget(add_btn)

        # Cart List Header
        cart_title = Label(
            text="[b]Current Cart Items[/b]",
            markup=True,
            size_hint_y=None,
            height=dp(30),
            color=(0.15, 0.15, 0.15, 1)
        )
        root.add_widget(cart_title)

        # Scrollable Cart List
        scroll = ScrollView(size_hint=(1, 1))
        self.cart_layout = GridLayout(cols=1, spacing=dp(5), size_hint_y=None)
        self.cart_layout.bind(minimum_height=self.cart_layout.setter('height'))
        scroll.add_widget(self.cart_layout)
        root.add_widget(scroll)

        # Total Display
        self.total_label = Label(
            text="[b]Total: 0 MMK[/b]",
            markup=True,
            font_size=dp(20),
            size_hint_y=None,
            height=dp(45),
            color=(0.05, 0.5, 0.2, 1)
        )
        root.add_widget(self.total_label)

        # Bottom Action Buttons
        btn_bar = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))

        clear_btn = Button(
            text="Clear",
            background_color=(0.85, 0.25, 0.25, 1),
            bold=True
        )
        clear_btn.bind(on_press=self.clear_cart)

        history_btn = Button(
            text="History",
            background_color=(0.45, 0.45, 0.5, 1),
            bold=True
        )
        history_btn.bind(on_press=self.show_history)

        checkout_btn = Button(
            text="Checkout / Sale",
            background_color=(0.15, 0.68, 0.38, 1),
            bold=True
        )
        checkout_btn.bind(on_press=self.checkout)

        btn_bar.add_widget(clear_btn)
        btn_bar.add_widget(history_btn)
        btn_bar.add_widget(checkout_btn)
        root.add_widget(btn_bar)

        return root

    def add_to_cart(self, instance):
        name = self.item_name_input.text.strip()
        price_text = self.price_input.text.strip()
        qty_text = self.qty_input.text.strip()

        if not name or not price_text or not qty_text:
            self.show_popup("Input Error", "Please enter Item Name, Price, and Quantity.")
            return

        try:
            price = float(price_text)
            qty = int(qty_text)
            if price <= 0 or qty <= 0:
                raise ValueError
        except ValueError:
            self.show_popup("Invalid Number", "Price and Quantity must be greater than 0.")
            return

        subtotal = price * qty
        self.cart.append({"name": name, "price": price, "qty": qty, "subtotal": subtotal})

        self.item_name_input.text = ""
        self.price_input.text = ""
        self.qty_input.text = "1"
        self.refresh_cart()

    def refresh_cart(self):
        self.cart_layout.clear_widgets()
        total = 0
        for idx, item in enumerate(self.cart):
            total += item["subtotal"]
            row = BoxLayout(size_hint_y=None, height=dp(40), padding=[dp(5), 0])
            lbl = Label(
                text=f"{idx+1}. {item['name']} ({item['qty']} x {item['price']:,.0f}) = {item['subtotal']:,.0f} MMK",
                color=(0.1, 0.1, 0.1, 1),
                halign="left",
                valign="middle"
            )
            lbl.bind(size=lbl.setter('text_size'))
            row.add_widget(lbl)

            del_btn = Button(
                text="X",
                size_hint_x=None,
                width=dp(36),
                background_color=(0.9, 0.3, 0.3, 1)
            )
            del_btn.bind(on_press=lambda btn, i=idx: self.remove_item(i))
            row.add_widget(del_btn)
            self.cart_layout.add_widget(row)

        self.total_label.text = f"[b]Total: {total:,.0f} MMK[/b]"

    def remove_item(self, index):
        if 0 <= index < len(self.cart):
            self.cart.pop(index)
            self.refresh_cart()

    def clear_cart(self, instance):
        self.cart = []
        self.refresh_cart()

    def checkout(self, instance):
        if not self.cart:
            self.show_popup("Empty Cart", "Add items before checkout.")
            return

        total = sum(item["subtotal"] for item in self.cart)
        record = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "items": self.cart,
            "total": total
        }

        history = []
        if os.path.exists(self.sales_history_file):
            try:
                with open(self.sales_history_file, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except Exception:
                history = []

        history.append(record)
        with open(self.sales_history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

        self.cart = []
        self.refresh_cart()
        self.show_popup("Sale Completed!", f"Receipt saved!\nTotal Paid: {total:,.0f} MMK")

    def show_history(self, instance):
        if not os.path.exists(self.sales_history_file):
            self.show_popup("Sales History", "No sales recorded yet.")
            return

        with open(self.sales_history_file, "r", encoding="utf-8") as f:
            history = json.load(f)

        if not history:
            self.show_popup("Sales History", "No sales recorded yet.")
            return

        lines = []
        grand_total = 0
        for rec in history[-10:]:
            grand_total += rec["total"]
            lines.append(f"{rec['timestamp']} -> {rec['total']:,.0f} MMK ({len(rec['items'])} items)")

        summary = "\n".join(lines) + f"\n\nRecent 10 Sales Total: {grand_total:,.0f} MMK"
        self.show_popup("Recent Sales History", summary)

    def show_popup(self, title, message):
        box = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        lbl = Label(text=message)
        btn = Button(text="OK", size_hint_y=None, height=dp(40))
        box.add_widget(lbl)
        box.add_widget(btn)
        popup = Popup(title=title, content=box, size_hint=(0.85, 0.45))
        btn.bind(on_press=popup.dismiss)
        popup.open()


if __name__ == "__main__":
    POSApp().run()
