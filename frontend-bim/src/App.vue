<template>
  <div class="login-wrapper">
    <div class="login-card">
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
            <!-- Aquí hacemos la magia: alternamos el tipo de input -->
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
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const username = ref('')
const password = ref('')
const errorMessage = ref('')
const isLoading = ref(false)

// Nueva variable reactiva para controlar la visibilidad
const showPassword = ref(false)

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

    alert('Autenticación exitosa. Token registrado en el navegador.')

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

h2 {
  margin-bottom: 0.5rem;
  color: #2c3e50;
}

.subtitle {
  color: #7f8c8d;
  margin-bottom: 2rem;
  font-size: 0.9rem;
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

/* Nuevos estilos para el campo de contraseña */
.password-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.password-wrapper input {
  padding-right: 80px; /* Dejamos espacio para el botón */
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

/* Estilos del botón de envío */
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