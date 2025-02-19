---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.4
  kernelspec:
    display_name: qutip-dev
    language: python
    name: python3
---

### Roots of Parametric Polynomials

On of my recent endless scrolls to social media, I encountered beautiful 
animations from Professor Simone Conradi, showing the roots of parametric 
polynomials in the complex plane. Inspired by their beauty and giving myself an
excuse to use jax. I decided to make my on animation 

```python
import jax
import jax.numpy as jnp
import os
os.environ["XLA_PYTHON_CLIENT_PREALLOCATE"] = "false"
```

Consider the parametric polynomial

$f(x)= |t|x^{14}  +(t^{5}+i t^{2}+t+5) x^{10} + (t^{2}+1) x^{5} + 2 $

```python
# @jax.jit
# def polynomial(ts,a):
#     coeffs = lambda t: jnp.array([1,jnp.abs(t)**2 -t,t**11 - abs(t)**10,0,(a*t**5 - 12j*t**2 -1),0,0,0,0,(a*t**3+5*t**2 - 1),0,0,0,0,-6*abs(t)])
#     func1=jax.vmap(lambda t,a: jnp.roots(coeffs(t,a),strip_zeros=False))
#     func2=jax.vmap(lambda a:func1(ts,a))
#     return jnp.nan_to_num(func2(a))
    
```

```python
from jax import random
key = random.key(42)
key2 = random.key(84)
```

```python
def polynomial_coeffs(t, a):
    return jnp.array([a, (a**2), (-a)**3, 0, (5*a*t**5 - 1.2*a*1j*t**2 - 1), 0, 0, a**2-a, 0, (a*t**3 + a*t**2 - 2), 0, 5*a-1, t**2, 0, -t])

def compute_roots_for_single_a(a, ts):
    def roots_for_single_t(t):
        coeffs = polynomial_coeffs(t, a)
        return jnp.roots(coeffs, strip_zeros=False)
    
    return jax.vmap(roots_for_single_t)(ts)

@jax.jit
def polynomial(ts, as_):
    return jnp.nan_to_num(jax.vmap(lambda a: compute_roots_for_single_a(a, ts))(as_))
```

```python
import numpy as np
result=[]
j=0.5
while j<2:
    x=random.uniform(key, shape=(5000,))
    y=random.uniform(key2, shape=(5000,))
    a=jnp.linspace(-1+j,-0.9+j,25)
    z=x+1j*y
    j+=0.1
    one=polynomial(z,a)
    result.append(np.array(one))
    print(j)
answer=np.concatenate(result,axis=0)

```

The plot is nice, I want to include more points and make the visualization nicer, in a similar way to the tweet

```python
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
# Assuming 'one' is your array of roots from the polynomial function
# If it's not defined, you'll need to calculate it using your polynomial function

fig, ax = plt.subplots(figsize=(8, 8))
scatter = ax.scatter([], [], s=0.0005, cmap='viridis')

# Set the axis limits (adjust these based on your data)
#ax.set_xlim(jnp.real(one).min() - 0.1, jnp.real(one).max() + 0.1)
#ax.set_ylim(jnp.imag(one).min() - 0.1, jnp.imag(one).max() + 0.1)
al=2.4
b=2
ax.set_xlim(-al - 0.01*al, al + 0.01*al)
ax.set_ylim(-b- 0.01*b, b + 0.01*b)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.xaxis.set_ticks([])
ax.yaxis.set_ticks([])
fig.patch.set_facecolor('beige')  # Figure background color
ax.set_facecolor('beige')       # Axes background color
plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

def animate(frame):
    one2 = np.array(answer[frame]).flatten()  # Replace np with jnp if needed
    real_vals = np.real(one2)
    imag_vals = np.imag(one2)
    
    # Compute the absolute values for coloring
    colors = np.abs(one2)

    # Update scatter plot with new points and colors
    scatter.set_offsets(np.column_stack((real_vals, imag_vals)))
    scatter.set_array(colors)  # Set the color array to map to point absolute values
    
    return scatter,
anim = FuncAnimation(fig, animate, frames=len(answer), interval=5, blit=True)

# Uncomment the next line to save the animation
anim.save('polynomial_roots.gif', writer='pillow', fps=50)

plt.show()
```

```python
from IPython.display import Image
Image(open('polynomial_roots.gif','rb').read())

```

TODO:

- Make animation prettier perhaps with manim
- Use the polynomial from the tweets or something prettier
- Make another file with some fractal
- Refactor the polynomial code so you get some jax practice

```python

```

```python

```
