import cv2
import numpy as np
import subprocess
#Rango de colores en HSV para identificar "inquilinos conocidos"
rangos_hsv = {"Elefante": ([90, 50, 50], [130, 255, 255]), #azul 
			"Unicornio": ([20, 100, 100], [40, 255, 255]), #Amarillo
			"Pinguino": ([0, 0, 0],[180, 255, 50]) #Negro
			}
			
#Comenzar la deteccion en tiempo real
print("Iniciando camara... Asegurar buena iluminacion para mejor precision de reconocimiento")
pipe = subprocess.Popen(["libcamera-vid", "-t", "0", "--width","640", "--height", "480", "--framerate", "30", "--codec", "yuv420", "-o", "-"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
frame_size = int(640 * 480 * 1.5)

while True:
	#Leer un frame
	raw_frame = pipe.stdout.read(frame_size)
	if len(raw_frame) != frame_size:
		print("Error: No se pudo leer el frame.")
		break
	yuv = np.frombuffer(raw_frame, dtype=np.uint8).reshape(int(480 * 1.5), 640)
	frame = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR_I420)
	#Convertir a HSV
	hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
	
	#Verificar presencia de colores
	objeto_detectado = "No reconocido"
	color_detectado = (0, 0, 255)
	
	for nombre, (lower, upper) in rangos_hsv.items():
		mascara = cv2.inRange(hsv, np.array(lower), np.array(upper))
		if cv2.countNonZero(mascara) > 500: #Ajustar el umbral si es necesario
			objeto_detectado = f"Inquilino conocido: {nombre}" if nombre != "Pinguino" else "Desconocido: Pinguino"
			color_detectado = (0, 255, 0) if nombre != "Pinguino" else (0, 0, 255)
			break
			
	#Mostrar el resultado solo si hay algo en la imagen 
	cv2.putText(frame, objeto_detectado, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color_detectado, 2)
	cv2.imshow("Reconocimiento por color", frame)
	
	#Salir del loop con la tecla q
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break
		

pipe.stdout.close()
cv2.destroyAllWindows()
