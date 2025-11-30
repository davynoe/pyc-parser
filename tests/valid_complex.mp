def max(a, b) {
  if (a > b) {
    return a;
  } else {
    return b;
  }
}

def min(a, b) {
  if (a < b) {
    return a;
  } else {
    return b;
  }
}

x = 15;
y = 20;
z = max(x, y);
w = min(x, y);
print(z);
print(w);

