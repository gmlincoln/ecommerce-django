
class Cart:
 def __init__(self,request):
  self.session=request.session
  self.cart=self.session.get('cart',{})
 def add(self,id,price):
  id=str(id)
  self.cart.setdefault(id,{'qty':0,'price':str(price)})
  self.cart[id]['qty']+=1
  self.save()
 def update(self,id,qty):
  id=str(id)
  if id in self.cart: self.cart[id]['qty']=qty
  self.save()
 def remove(self,id):
  id=str(id)
  if id in self.cart: del self.cart[id]
  self.save()
 def save(self):
  self.session['cart']=self.cart
  self.session.modified=True
