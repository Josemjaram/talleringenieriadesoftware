<template>
  <div class="page">
    <!-- Se muestra el título principal del taller -->
    <h1 class="title">TALLER WEB</h1>

    <!-- Se organiza el panel en una cuadrícula de cuatro columnas -->
    <div class="grid">
      <!-- Registro -->
      <div class="card">
        <h2>Registro</h2>
        <!-- Se captura email/contraseña y se envía al backend /register -->
        <form @submit.prevent="handleRegister" class="form">
          <input type="email" v-model="registerEmail" placeholder="Email" required />
          <input type="password" v-model="registerPassword" placeholder="Contraseña" required />
          <button type="submit" class="btn">Registrarse</button>
        </form>
        <!-- Se muestra mensaje de resultado -->
        <div v-if="registerMsg" :class="['msg', registerOk ? 'success' : 'error']">
          {{ registerMsg }}
        </div>
      </div>

      <!-- Login -->
      <div class="card">
        <h2>Login</h2>
        <!-- Se valida contra /login (incluye usuario fijo y los registrados) -->
        <form @submit.prevent="handleLogin" class="form">
          <input type="email" v-model="loginEmail" placeholder="Email" required />
          <input type="password" v-model="loginPassword" placeholder="Contraseña" required />
          <button type="submit" class="btn">Iniciar sesión</button>
        </form>
        <div v-if="loginMsg" :class="['msg', loginOk ? 'success' : 'error']">
          {{ loginMsg }}
        </div>
      </div>

      <!-- Cambiar contraseña -->
      <div class="card">
        <h2>Cambiar contraseña</h2>
        <!-- Se valida primero con /login y luego se aplica PUT /users/:email -->
        <form @submit.prevent="handleChangePassword" class="form">
          <input type="email" v-model="cpEmail" placeholder="Email" required />
          <input type="password" v-model="cpOldPassword" placeholder="Contraseña actual" required />
          <input type="text" v-model="cpNewPassword" placeholder="Nueva contraseña (visible)" required />
          <button type="submit" class="btn">Cambiar</button>
        </form>
        <div v-if="cpMsg" :class="['msg', cpOk ? 'success' : 'error']">
          {{ cpMsg }}
        </div>
      </div>

      <!-- Eliminar usuario -->
      <div class="card">
        <h2>Eliminar usuario</h2>
        <!-- Se valida primero con /login y luego se aplica DELETE /users/:email -->
        <form @submit.prevent="handleDeleteUser" class="form">
          <input type="email" v-model="delEmail" placeholder="Email" required />
          <input type="password" v-model="delPassword" placeholder="Contraseña" required />
          <button type="submit" class="btn">Eliminar</button>
        </form>
        <div v-if="delMsg" :class="['msg', delOk ? 'success' : 'error']">
          {{ delMsg }}
        </div>
      </div>
    </div>

    <hr />

    <!-- Usuarios registrados -->
    <div class="users">
      <div class="users-header">
        <h2>Usuarios registrados</h2>
        <!-- Se actualiza el listado desde /users -->
        <button class="btn small" @click="loadUsers">Refrescar</button>
      </div>
      <div v-if="usersError" class="msg error">{{ usersError }}</div>
      <ul v-else class="users-list">
        <li v-for="u in users" :key="u.email">{{ u.email }}</li>
        <li v-if="users.length === 0" class="muted">No hay usuarios.</li>
      </ul>
    </div>
  </div>
</template>

<script>
// Se define URL base del backend
const API = "http://127.0.0.1:5000";

export default {
  name: "App",

  // Se definen estados del formulario y del listado
  data() {
    return {
      // Registro
      registerEmail: "",
      registerPassword: "",
      registerMsg: "",
      registerOk: false,

      // Login
      loginEmail: "",
      loginPassword: "",
      loginMsg: "",
      loginOk: false,

      // Cambiar contraseña
      cpEmail: "",
      cpOldPassword: "",
      cpNewPassword: "",
      cpMsg: "",
      cpOk: false,

      // Eliminar
      delEmail: "",
      delPassword: "",
      delMsg: "",
      delOk: false,

      // Usuarios
      users: [],
      usersError: "",
    };
  },

  // Se carga el listado inicial al montar el componente
  mounted() {
    this.loadUsers();
  },

  methods: {
    // ---------- Registro ----------
    // Se envían datos a /register para crear usuario
    async handleRegister() {
      this.registerMsg = "";
      this.registerOk = false;
      try {
        const res = await fetch(`${API}/register`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            email: this.registerEmail.trim(),
            password: this.registerPassword,
          }),
        });
        const data = await res.json().catch(() => ({}));
        this.registerOk = res.ok;
        this.registerMsg = data.msg || (res.ok ? "Registro completado." : "Error en registro");
        if (res.ok) {
          this.registerEmail = "";
          this.registerPassword = "";
          this.loadUsers();
        }
      } catch {
        this.registerMsg = "Error de conexión o servidor.";
      }
    },

    // ---------- Login ----------
    // Se validan credenciales contra /login
    async handleLogin() {
      this.loginMsg = "";
      this.loginOk = false;
      try {
        const res = await fetch(`${API}/login`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            email: this.loginEmail.trim(),
            password: this.loginPassword,
          }),
        });
        const data = await res.json().catch(() => ({}));
        this.loginOk = res.ok;
        this.loginMsg = data.msg || (res.ok ? "Login exitoso." : "Error en login");
      } catch {
        this.loginMsg = "Error de conexión o servidor.";
      }
    },

    // ---------- Cambiar contraseña ----------
    // Se valida con /login y luego se actualiza con PUT /users/:email
    async handleChangePassword() {
      this.cpMsg = "";
      this.cpOk = false;
      try {
        const check = await fetch(`${API}/login`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            email: this.cpEmail.trim(),
            password: this.cpOldPassword,
          }),
        });

        if (!check.ok) {
          const err = await check.json().catch(() => ({}));
          this.cpMsg = err.msg || "Credenciales inválidas";
          return;
        }

        const res = await fetch(`${API}/users/${encodeURIComponent(this.cpEmail.trim())}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ password: this.cpNewPassword }),
        });
        const data = await res.json().catch(() => ({}));
        this.cpOk = res.ok;
        this.cpMsg = data.msg || (res.ok ? "Contraseña actualizada." : "No se pudo actualizar");

        if (res.ok) {
          this.cpEmail = "";
          this.cpOldPassword = "";
          this.cpNewPassword = "";
          this.loadUsers();
        }
      } catch {
        this.cpMsg = "Error de conexión o servidor.";
      }
    },

    // ---------- Eliminar usuario ----------
    // Se valida con /login y luego se elimina con DELETE /users/:email
    async handleDeleteUser() {
      this.delMsg = "";
      this.delOk = false;
      try {
        const check = await fetch(`${API}/login`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            email: this.delEmail.trim(),
            password: this.delPassword,
          }),
        });

        if (!check.ok) {
          const err = await check.json().catch(() => ({}));
          this.delMsg = err.msg || "Credenciales inválidas";
          return;
        }

        const res = await fetch(`${API}/users/${encodeURIComponent(this.delEmail.trim())}`, {
          method: "DELETE",
        });
        const data = await res.json().catch(() => ({}));
        this.delOk = res.ok;
        this.delMsg = data.msg || (res.ok ? "Usuario eliminado." : "No se pudo eliminar");

        if (res.ok) {
          this.delEmail = "";
          this.delPassword = "";
          this.loadUsers();
        }
      } catch {
        this.delMsg = "Error de conexión o servidor.";
      }
    },

    // ---------- Listado ----------
    // Se consultan usuarios en /users para mostrarlos en pantalla
    async loadUsers() {
      this.usersError = "";
      try {
        const res = await fetch(`${API}/users`);
        if (!res.ok) {
          this.usersError = "No se pudieron cargar los usuarios.";
          return;
        }
        const data = await res.json();
        this.users = data.items || [];
      } catch {
        this.usersError = "Error de conexión o servidor.";
      }
    },
  },
};
</script>

<style scoped>
/* Se define contenedor principal y espaciados */
.page {
  max-width: 1100px;
  margin: 24px auto 60px;
  padding: 0 16px;
}

/* Se establece título grande y blanco intenso, con leve brillo */
.title {
  text-align: center;
  font-size: 2.8rem;         /* más grande */
  color: #ffffff;            /* blanco brillante */
  text-shadow: 0 0 8px rgba(255,255,255,0.5); /* realce sutil */
  letter-spacing: 1px;
  margin-bottom: 22px;
}

/* Se configura cuadrícula para las cuatro tarjetas */
.grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(220px, 1fr));
  gap: 16px;
}

/* Se define estilo de tarjetas con fondo negro y borde blanco */
.card {
  background: #000;          /* fondo negro */
  color: #fff;               /* texto blanco para contraste */
  border: 1px solid #fff;    /* borde blanco */
  border-radius: 10px;
  padding: 16px;
  box-shadow: 0 2px 8px #0006;
}
.card h2 {
  font-size: 1.05rem;
  margin-bottom: 10px;
}

/* Se define columna de formulario */
.form {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

/* Se establecen inputs en negro con borde blanco y texto claro */
input {
  padding: 8px;
  background: #111;
  color: #f5f5f5;
  border: 1px solid #fff;
  border-radius: 6px;
  font-size: 0.98rem;
}
input::placeholder {
  color: #cccccc;
}

/* Se definen botones rojos */
.btn {
  padding: 9px 10px;
  background: #e11d48;       /* rojo */
  color: #fff;
  border: none;
  border-radius: 6px;
  font-weight: 700;
  cursor: pointer;
  transition: transform .03s ease, box-shadow .2s ease, background .2s ease;
}
.btn:hover {
  background: #be123c;       /* rojo más oscuro */
}
.btn:active {
  transform: translateY(1px);
}
.btn.small {
  padding: 6px 10px;
  font-size: 0.9rem;
}

/* Se definen mensajes de estado (verde/rojo) */
.msg {
  margin-top: 8px;
  border-radius: 6px;
  padding: 8px 10px;
  font-size: 0.95rem;
  border: 1px solid transparent;
}
.msg.success {
  color: #185a2b;
  background: #e6ffed;
  border-color: #b5efc7;
}
.msg.error {
  color: #7a1122;
  background: #ffe6ea;     /* rojo suave */
  border-color: #f4b8c1;
}

/* Se define bloque de usuarios con el mismo esquema negro/blanco */
.users {
  margin-top: 26px;
  background: #000;          /* fondo negro */
  color: #fff;               /* texto blanco */
  border: 1px solid #fff;    /* borde blanco */
  border-radius: 10px;
  padding: 16px;
}
.users-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.users-list {
  margin: 12px 0 0;
  padding-left: 18px;
}
.muted {
  color: #cccccc;
}
hr {
  margin: 26px 0;
  border: none;
  border-top: 1px solid #444; /* separador tenue sobre fondo oscuro */
}

/* Se adapta la cuadrícula a pantallas pequeñas */
@media (max-width: 980px) {
  .grid {
    grid-template-columns: 1fr 1fr;
  }
}
@media (max-width: 520px) {
  .grid {
    grid-template-columns: 1fr;
  }
}
</style>
