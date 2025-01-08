import numpy as np
import keras
from main_PINN_train import PINNModel

model = keras.models.load_model('PINN_model_latest.h5')
# 假设我们想要预测从0度到45度的PID参数
new_target_angle = 40
new_input = np.array([[new_target_angle]])

# 使用模型预测PID参数
predicted_pid_params = model.predict(new_input)
print("Predicted PID parameters:", predicted_pid_params)