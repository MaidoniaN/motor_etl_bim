<template>
  <div class="login-wrapper">
    
    <!-- VISTA DE LOGIN (Se oculta si está autenticado) -->
    <div v-if="!isAuthenticated" class="login-card">
      <h2>Acceso Plataforma ETL BIM</h2>
      <p class="subtitle">Ingrese sus credenciales de administración</p>

      <form @submit.prevent="handleLogin">
        <div class="input-group">
          <label for="username">Usuario</label>
          <input 
            id="username" 
            v-model="username" 
            type="text" 
            required 
            placeholder="ej. admin"
          />
        </div>

        <div class="input-group">
          <label for="password">Contraseña</label>
          <div class="password-wrapper">
            <input 
              id="password" 
              v-model="password" 
              :type="showPassword ? 'text' : 'password'" 
              required 
              placeholder="••••••"
            />
            <button 
              type="button" 
              class="toggle-password-btn" 
              @click="showPassword = !showPassword"
            >
              {{ showPassword ? 'Ocultar' : 'Mostrar' }}
            </button>
          </div>
        </div>

        <button type="submit" class="submit-btn" :disabled="isLoading">
          {{ isLoading ? 'Conectando...' : 'Ingresar' }}
        </button>
      </form>

      <div v-if="errorMessage" class="error-message">
        {{ errorMessage }}
      </div>
    </div>

    <!-- VISTA DEL DASHBOARD (Aparece tras el login exitoso) -->
    <div v-else class="login-card dashboard-card">
      <h2>Panel de Control BIM</h2>
      <p class="subtitle">Sesión activa. Escuchando eventos del ratón y teclado.</p>
      
      <div class="info-box">
        Si no interactúas con la pantalla en 15 minutos, tu sesión expirará automáticamente por seguridad.
      </div>

      <button @click="cerrarSesionPorInactividad(true)" class="submit-btn logout-btn">
        Cerrar Sesión Manual
      </button>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'

const username = ref('')
const password = ref('')
const errorMessage = ref('')
const isLoading = ref(false)
const showPassword = ref(false)

// Estado para controlar si el usuario está dentro de la plataforma
const isAuthenticated = ref(false)

// ==========================================
// LÓGICA DE SEGURIDAD: INACTIVIDAD
// ==========================================
let timeoutInactividad;
const TIEMPO_MAXIMO_INACTIVIDAD = 15 * 60 * 1000; // 15 minutos en milisegundos

const cerrarSesionPorInactividad = (esManual = false) => {
  // 1. Borramos el token de localStorage
  localStorage.removeItem('etl_access_token');
  
  // 2. Eliminamos el token de los headers por defecto de Axios
  delete axios.defaults.headers.common['Authorization'];
  
  // 3. Reseteamos el estado para volver al formulario
  isAuthenticated.value = false;
  username.value = '';
  password.value = '';
  
  // 4. Mensaje informativo (solo si fue por inactividad)
  if (!esManual) {
    errorMessage.value = 'Tu sesión ha expirado por inactividad. Por favor, ingresa nuevamente.';
  } else {
    errorMessage.value = '';
  }
}

const reiniciarTemporizador = () => {
  // Solo aplicamos el temporizador si el usuario ya hizo login
  if (isAuthenticated.value) {
    clearTimeout(timeoutInactividad);
    timeoutInactividad = setTimeout(() => cerrarSesionPorInactividad(false), TIEMPO_MAXIMO_INACTIVIDAD);
  }
}

// Escuchamos los eventos globales del navegador
onMounted(() => {
  window.addEventListener('mousemove', reiniciarTemporizador);
  window.addEventListener('keydown', reiniciarTemporizador);
  window.addEventListener('click', reiniciarTemporizador);
  window.addEventListener('scroll', reiniciarTemporizador);
})

// Limpiamos los eventos si el componente se destruye (Buena práctica en Vue)
onUnmounted(() => {
  window.removeEventListener('mousemove', reiniciarTemporizador);
  window.removeEventListener('keydown', reiniciarTemporizador);
  window.removeEventListener('click', reiniciarTemporizador);
  window.removeEventListener('scroll', reiniciarTemporizador);
  clearTimeout(timeoutInactividad);
})

// ==========================================
// LÓGICA DE AUTENTICACIÓN
// ==========================================
const handleLogin = async () => {
  isLoading.value = true
  errorMessage.value = ''

  try {
    const response = await axios.post('http://127.0.0.1:8000/login', {
      username: username.value,
      password: password.value
    })

    const token = response.data.access_token
    localStorage.setItem('etl_access_token', token)
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`

    // Login exitoso: Cambiamos estado e iniciamos el conteo de inactividad
    isAuthenticated.value = true;
    reiniciarTemporizador();

  } catch (error) {
    if (error.response && error.response.status === 401) {
      errorMessage.value = 'Usuario o contraseña incorrectos.'
    } else if (error.response && error.response.status === 403) {
      errorMessage.value = 'El usuario se encuentra inactivo.'
    } else {
      errorMessage.value = 'Error al conectar con el motor backend.'
    }
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.login-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f4f7f6;
  font-family: sans-serif;
}

.login-card {
  background: white;
  padding: 2rem 3rem;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  width: 100%;
  max-width: 400px;
}

.dashboard-card {
  text-align: center;
}

h2 {
  margin-bottom: 0.5rem;
  color: #2c3e50;
}

.subtitle {
  color: #7f8c8d;
  margin-bottom: 2rem;
  font-size: 0.9rem;
}

.info-box {
  background-color: #e8f4f8;
  color: #2980b9;
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 2rem;
  font-size: 0.9rem;
  border: 1px solid #bce8f1;
}

.input-group {
  margin-bottom: 1.5rem;
  text-align: left;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  color: #34495e;
  font-weight: bold;
  font-size: 0.9rem;
}

input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #bdc3c7;
  border-radius: 4px;
  box-sizing: border-box;
}

.password-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.password-wrapper input {
  padding-right: 80px; 
}

.toggle-password-btn {
  position: absolute;
  right: 10px;
  background: none;
  border: none;
  color: #2980b9;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: bold;
}

.toggle-password-btn:hover {
  text-decoration: underline;
}

.submit-btn {
  width: 100%;
  padding: 0.75rem;
  background-color: #2980b9;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s;
}

.submit-btn:hover:not(:disabled) {
  background-color: #3498db;
}

.submit-btn:disabled {
  background-color: #95a5a6;
  cursor: not-allowed;
}

.logout-btn {
  background-color: #e74c3c;
}

.logout-btn:hover {
  background-color: #c0392b !important;
}

.error-message {
  margin-top: 1.5rem;
  padding: 0.75rem;
  background-color: #fee;
  color: #c0392b;
  border-radius: 4px;
  border: 1px solid #e74c3c;
  font-size: 0.9rem;
}
</style>