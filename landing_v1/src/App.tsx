import React, { useState, useEffect } from 'react';
import { 
  Scissors, 
  MapPin, 
  Phone, 
  Clock, 
  Star, 
  Menu, 
  X,
  Instagram,
  ArrowRight,
  CreditCard,
  DollarSign,
  Smartphone,
  Calendar
} from 'lucide-react';

import logo from "./Barba&Co_logo.png";


function App() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [scrollY, setScrollY] = useState(0);

  useEffect(() => {
    const handleScroll = () => setScrollY(window.scrollY);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const services = [
    { 
      name: 'Corte', 
      price: '$45', 
      duration: '45 min',
      description: 'Corte personalizado con consulta de estilo incluida'
    },
    { 
      name: 'Corte + Barba', 
      price: '$35', 
      duration: '30 min',
      description: 'Afeitado tradicional con toalla caliente y aceites premium'
    },
    { 
      name: 'Arreglo Barba', 
      price: '$30', 
      duration: '25 min',
      description: 'Diseño y mantenimiento profesional de barba'
    },
    { 
      name: 'Perfilado de cejas', 
      price: '$75', 
      duration: '60 min',
      description: 'Corte + afeitado + tratamiento facial completo'
    }
  ];


  return (
    <div className="min-h-screen bg-white overflow-x-hidden">

      {/* Navigation */}
      <nav
        className={`fixed w-full z-50 transition-all duration-500 ${
          scrollY > 50
            ? 'bg-white/95 backdrop-blur-xl shadow-sm border-b border-gray-100'
            : 'bg-transparent'
        }`}
      >
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            {/* Logo / Brand */}
            <div className="flex items-center space-x-3">
              {/* Ícono decorativo opcional (podés quitarlo si el logo ya lo incluye) 
                <div className="relative">
                  <Scissors
                    className={`h-7 w-7 transition-colors duration-300 ${
                      scrollY > 50 ? 'text-black' : 'text-white'
                    }`}
                  />
                  <div className="absolute -inset-2 bg-gradient-to-r from-gray-600 to-black rounded-full opacity-20 blur-sm"></div>
                </div>
              */}

              {/* Logo con link al inicio */}
              <a href="#inicio" className="flex items-center hover:opacity-80 transition-opacity">
                <img
                  src={logo}
                  alt="BARBA&CO Logo"
                  className={`h-8 md:h-10 object-contain transition-all duration-300 ${
                    scrollY > 50 ? 'brightness-0' : 'brightness-100'
                  }`}
                />
              </a>
            </div>


            {/* Desktop Menu */}
            <div className="hidden md:flex space-x-10">
              {[
                { label: 'Inicio', href: '#inicio' },
                { label: 'Servicios', href: '#servicios' },
                { label: 'Membresías', href: '#membresias' },
                { label: 'Métodos de Pago', href: '#pagos' },
                { label: 'Ubicación', href: '#ubicación' },
                { label: 'Contacto', href: '#contacto' },
                { label: 'Turnos Online', href: '#turnos' },
              ].map((item) => (
                <a
                  key={item.label}
                  href={item.href}
                  className={`text-sm font-light tracking-wide transition-all duration-300 hover:opacity-60 relative group ${
                    scrollY > 50 ? 'text-gray-700' : 'text-gray-200'
                  }`}
                >
                  {item.label}
                  <span className="absolute -bottom-1 left-0 w-0 h-px bg-current transition-all duration-300 group-hover:w-full"></span>
                </a>
              ))}
            </div>

            {/* Mobile Menu Button */}
            <button
              className={`md:hidden transition-colors duration-300 ${
                scrollY > 50 ? 'text-black' : 'text-white'
              }`}
              onClick={() => setIsMenuOpen(!isMenuOpen)}
            >
              {isMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>

          {/* Mobile Menu */}
          {isMenuOpen && (
            <div className="md:hidden bg-white/95 backdrop-blur-xl rounded-2xl mt-4 py-8 px-6 shadow-xl border border-gray-100">
              {[
                { label: 'Inicio', href: '#inicio' },
                { label: 'Servicios', href: '#servicios' },
                { label: 'Membresías', href: '#membresias' },
                { label: 'Métodos de Pago', href: '#pagos' },
                { label: 'Ubicación', href: '#ubicación' },
                { label: 'Contacto', href: '#contacto' },
                { label: 'Turnos Online', href: '#turnos' },
              ].map((item) => (
                <a
                  key={item.label}
                  href={item.href}
                  className="block py-3 text-gray-700 font-light tracking-wide hover:opacity-60 transition-opacity"
                  onClick={() => setIsMenuOpen(false)}
                >
                  {item.label}
                </a>
              ))}
            </div>
          )}
        </div>
      </nav>

      {/* Hero Section */}
      <section id="inicio" className="relative min-h-screen flex items-center justify-center bg-gradient-to-b from-black via-gray-900 to-gray-50">

        <div className="relative z-10 text-center px-6 lg:px-8 max-w-5xl mx-auto">
          <div className="mb-8">
            <div className="inline-block p-4 rounded-full bg-white/10 backdrop-blur-sm mb-6">
              <Scissors className="h-12 w-12 text-white" />
            </div>
          </div>

          {/* Nuevo título */}
          {/*
            <h1 className="text-6xl md:text-8xl font-extralight text-white mb-8 leading-none tracking-tight">
              BARBA<span className="font-thin text-gray-300">&CO</span>
              <span className="block font-thin text-gray-300 text-5xl md:text-7xl mt-2">
                ESTILO Y PRECISIÓN
              </span>
            </h1>
          */}

          {/* Nuevo título */}
          <div className="mb-8 flex flex-col items-center">
            <img src={logo} alt="BARBA&CO Logo" className="h-24 md:h-32 mb-4 object-contain" />
          </div>

          {/* Nueva frase de bienvenida */}
          <p className="text-xl md:text-2xl text-gray-300 mb-12 max-w-3xl mx-auto font-light leading-relaxed">
            Tu barbería en Avellaneda. Donde el estilo se perfecciona con técnica, precisión y pasión.
          </p>

          <div className="flex flex-col sm:flex-row gap-6 justify-center items-center">
            <button
              onClick={() => window.open(
                "https://www.fresha.com/es/a/barba-co-pineyro-avenida-presidente-bernardino-rivadavia-215-o1ukwtm0/all-offer?menu=true&pId=1429418",
                "_blank"
              )}
              className="group bg-white text-black px-10 py-4 rounded-full font-light tracking-wide hover:bg-gray-100 transition-all duration-300 transform hover:scale-105 flex items-center space-x-2"
            >
              <span>Reservar Turno</span>
              <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
            </button>
            <button className="border border-white/30 text-white px-10 py-4 rounded-full font-light tracking-wide hover:bg-white/10 transition-all duration-300 backdrop-blur-sm">
              Ver Servicios
            </button>
          </div>
        </div>

        {/* Scroll indicator */}
        <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2">
          <div className="w-px h-16 bg-gradient-to-b from-white to-transparent"></div>
        </div>
      </section>

      {/* Services Section */}
      <section id="servicios" className="py-32 bg-gray-50">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="text-center mb-20">
            <div className="inline-block p-3 rounded-full bg-black/5 mb-6">
              <Scissors className="h-8 w-8 text-gray-600" />
            </div>
            <h2 className="text-5xl md:text-6xl font-extralight text-black mb-6 tracking-tight">
              Servicios
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto font-light leading-relaxed">
              Cada servicio está diseñado para ofrecer una experiencia única y personalizada.
              <br />
              <span className="block mt-3 text-gray-500">
                Hacemos cortes para adultos, niños y grupos.
              </span>
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-5xl mx-auto">
            {services.map((service, index) => (
              <div 
                key={index} 
                className="group bg-white p-10 rounded-3xl shadow-sm hover:shadow-xl transition-all duration-500 border border-gray-100 hover:border-gray-200"
              >
                <div className="flex justify-between items-start mb-6">
                  <div>
                    <h3 className="text-2xl font-light text-black mb-2 tracking-wide">
                      {service.name}
                    </h3>
                    <p className="text-gray-500 text-sm font-light tracking-wide">
                      {service.duration}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-3xl font-extralight text-black">
                      {service.price}
                    </p>
                  </div>
                </div>
                
                <p className="text-gray-600 font-light leading-relaxed mb-6">
                  {service.description}
                </p>
                
                <div className="flex items-center text-black group-hover:translate-x-2 transition-transform duration-300">
                  <span className="text-sm font-light tracking-wide">Reservar</span>
                  <ArrowRight className="h-4 w-4 ml-2" />
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Membership Section */}
      <section id="membresias" className="py-32 bg-gray-50">
        <div className="max-w-7xl mx-auto px-6 lg:px-8 text-center">
          <div className="inline-block p-3 rounded-full bg-black/5 mb-6">
            <CreditCard className="h-8 w-8 text-gray-600" />
          </div>

          <h2 className="text-5xl md:text-6xl font-extralight text-black mb-6 tracking-tight">
            ¿Cómo funciona una membresía?
          </h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto font-light leading-relaxed mb-16">
            Disfrutá de beneficios exclusivos y más flexibilidad en tus servicios.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-12 max-w-5xl mx-auto">
            {/* Paso 1 */}
            <div className="bg-white p-10 rounded-3xl shadow-sm hover:shadow-xl transition-all duration-500 border border-gray-100 hover:border-gray-200">
              <div className="flex justify-center mb-6">
                <DollarSign className="h-10 w-10 text-gray-700" />
              </div>
              <h3 className="text-2xl font-light text-black mb-3 tracking-wide">1. Comprás la membresía</h3>
              <p className="text-gray-600 font-light leading-relaxed">
                Elegí tu plan y pagalo por anticipado en el local o mediante nuestros métodos de pago.
              </p>
            </div>

            {/* Paso 2 */}
            <div className="bg-white p-10 rounded-3xl shadow-sm hover:shadow-xl transition-all duration-500 border border-gray-100 hover:border-gray-200">
              <div className="flex justify-center mb-6">
                <Scissors className="h-10 w-10 text-gray-700" />
              </div>
              <h3 className="text-2xl font-light text-black mb-3 tracking-wide">2. Recibís 4 servicios</h3>
              <p className="text-gray-600 font-light leading-relaxed">
                Usalos cuando quieras dentro de los 45 días desde tu primer turno.
              </p>
            </div>

            {/* Paso 3 */}
            <div className="bg-white p-10 rounded-3xl shadow-sm hover:shadow-xl transition-all duration-500 border border-gray-100 hover:border-gray-200">
              <div className="flex justify-center mb-6">
                <Star className="h-10 w-10 text-gray-700" />
              </div>
              <h3 className="text-2xl font-light text-black mb-3 tracking-wide">3. Disfrutá tu membresía</h3>
              <p className="text-gray-600 font-light leading-relaxed">
                Mantené tu look siempre impecable con la comodidad de ser parte de Barba Company. <br />
                <span className="block mt-4 text-black font-light">Solicitalo en el local.</span>
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Payment Methods Section */}
      <section id="pagos" className="py-32 bg-gray-50">
        <div className="max-w-7xl mx-auto px-6 lg:px-8 text-center">
          <div className="inline-block p-3 rounded-full bg-black/5 mb-6">
            <CreditCard className="h-8 w-8 text-gray-600" />
          </div>

          <h2 className="text-5xl md:text-6xl font-extralight text-black mb-6 tracking-tight">
            Métodos de pago
          </h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto font-light leading-relaxed mb-16">
            Elegí la forma de pago que más te convenga. Rápido, simple y sin complicaciones.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-12 max-w-5xl mx-auto">
            {/* Efectivo */}
            <div className="bg-white p-10 rounded-3xl shadow-sm hover:shadow-xl transition-all duration-500 border border-gray-100 hover:border-gray-200">
              <div className="flex justify-center mb-6">
                <DollarSign className="h-10 w-10 text-gray-700" />
              </div>
              <h3 className="text-2xl font-light text-black mb-3 tracking-wide">Efectivo</h3>
              <p className="text-gray-600 font-light leading-relaxed">
                Pagá directamente en el local y obtené el mejor precio disponible.
              </p>
            </div>

            {/* Tarjetas */}
            <div className="bg-white p-10 rounded-3xl shadow-sm hover:shadow-xl transition-all duration-500 border border-gray-100 hover:border-gray-200">
              <div className="flex justify-center mb-6">
                <CreditCard className="h-10 w-10 text-gray-700" />
              </div>
              <h3 className="text-2xl font-light text-black mb-3 tracking-wide">Tarjetas</h3>
              <p className="text-gray-600 font-light leading-relaxed">
                Aceptamos todas las tarjetas de crédito y débito. <br />
                <span className="text-gray-500 text-sm">(10% de recargo)</span>
              </p>
            </div>

            {/* Mercado Pago */}
            <div className="bg-white p-10 rounded-3xl shadow-sm hover:shadow-xl transition-all duration-500 border border-gray-100 hover:border-gray-200">
              <div className="flex justify-center mb-6">
                <Smartphone className="h-10 w-10 text-gray-700" />
              </div>
              <h3 className="text-2xl font-light text-black mb-3 tracking-wide">Mercado Pago</h3>
              <p className="text-gray-600 font-light leading-relaxed">
                Pagá con QR o transferencia desde la app de Mercado Pago. Simple y rápido.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Location Section */}
      <section id="ubicación" className="py-32 bg-gray-50">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-20 items-center">

            {/* Columna izquierda */}
            <div className="space-y-16">
              {/* Bloque Encontranos */}
              <div>
                <div className="flex items-center space-x-4 mb-8">
                  <div className="p-3 rounded-full bg-black/5 flex items-center justify-center">
                    <MapPin className="h-8 w-8 text-gray-600" />
                  </div>
                  <h2 className="text-5xl md:text-6xl font-extralight text-black tracking-tight leading-tight">
                    Encontranos
                  </h2>
                </div>

                <div className="bg-gray-100 p-8 rounded-3xl shadow-sm border border-gray-200">
                  <h3 className="text-2xl font-light text-black mb-6 tracking-wide">Dirección</h3>
                  <p className="text-lg text-gray-700 font-light mb-4">
                    Av. Pres. Bernardino Rivadavia 215<br />
                    Avellaneda, Buenos Aires, Argentina
                  </p>
                  <a
                    href="https://www.google.com/maps/place/Av.+Pres.+Bernardino+Rivadavia+215,+Avellaneda,+Provincia+de+Buenos+Aires"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center space-x-2 text-black hover:opacity-60 transition-opacity"
                  >
                    <MapPin className="h-4 w-4" />
                    <span className="text-sm font-light tracking-wide">Ver en Google Maps</span>
                  </a>
                </div>
              </div>

              {/* Bloque Horarios */}
              <div>
                <div className="flex items-center space-x-4 mb-8">
                  <div className="p-3 rounded-full bg-black/5 flex items-center justify-center">
                    <Clock className="h-8 w-8 text-gray-600" />
                  </div>
                  <h2 className="text-4xl md:text-5xl font-extralight text-black tracking-tight leading-tight">
                    Horarios de atención
                  </h2>
                </div>

                <div className="bg-gray-100 p-8 rounded-3xl shadow-sm border border-gray-200">
                  <h3 className="text-2xl font-light text-black mb-4 tracking-wide">Lunes a Sábado</h3>
                  <p className="text-lg text-gray-700 font-light">
                    11:00 a 20:00 hs
                  </p>
                </div>
              </div>
            </div>

            {/* Columna derecha - Mapa */}
            <div className="bg-white rounded-3xl shadow-inner overflow-hidden h-96 lg:h-[500px]">
              <iframe
                title="Ubicación Barbería"
                src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3283.876930184992!2d-58.36650822425733!3d-34.60726947295395!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x95bccd5d9d68cc5b%3A0xb7eec6b2b558cd1f!2sAv.%20Pres.%20Bernardino%20Rivadavia%20215%2C%20B1870CBE%20Avellaneda%2C%20Provincia%20de%20Buenos%20Aires!5e0!3m2!1ses-419!2sar!4v1730739000000!5m2!1ses-419!2sar"
                width="100%"
                height="100%"
                style={{ border: 0 }}
                allowFullScreen
                loading="lazy"
                referrerPolicy="no-referrer-when-downgrade"
              ></iframe>
            </div>
          </div>
        </div>
      </section>

      {/* Contact Section */}
      <section id="contacto" className="py-32 bg-gray-50">
        <div className="max-w-6xl mx-auto px-6 lg:px-8 text-center">
          <div className="inline-block p-3 rounded-full bg-black/5 mb-6">
            <Phone className="h-8 w-8 text-gray-600" />
          </div>

          <h2 className="text-5xl md:text-6xl font-extralight text-black mb-6 tracking-tight">
            Contáctanos
          </h2>

          <p className="text-xl text-gray-600 mb-16 font-light leading-relaxed max-w-2xl mx-auto">
            Elegí el medio que prefieras para comunicarte con nosotros o agendar tu próximo turno.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-10 max-w-4xl mx-auto">
            {/* Instagram */}
            <a
              href="https://www.instagram.com/barba.company/"
              target="_blank"
              rel="noopener noreferrer"
              className="group bg-white p-12 rounded-3xl shadow-md border border-gray-100 hover:shadow-xl transition-all duration-500 flex flex-col items-center justify-center space-y-6 hover:border-gray-200"
            >
              <div className="w-20 h-20 rounded-2xl bg-gray-50 flex items-center justify-center group-hover:bg-gray-100 transition-colors">
                <Instagram className="h-10 w-10 text-gray-700" />
              </div>
              <div>
                <h3 className="text-2xl font-light text-black mb-2 tracking-wide">Instagram</h3>
                <p className="text-gray-600 font-light">
                  Seguinos para ver los últimos cortes, estilos y promociones.
                </p>
              </div>
            </a>

            {/* WhatsApp */}
            <a
              href="https://wa.me/5491123456789"
              target="_blank"
              rel="noopener noreferrer"
              className="group bg-white p-12 rounded-3xl shadow-md border border-gray-100 hover:shadow-xl transition-all duration-500 flex flex-col items-center justify-center space-y-6 hover:border-gray-200"
            >
              <div className="w-20 h-20 rounded-2xl bg-gray-50 flex items-center justify-center group-hover:bg-gray-100 transition-colors">
                <Phone className="h-10 w-10 text-gray-700" />
              </div>
              <div>
                <h3 className="text-2xl font-light text-black mb-2 tracking-wide">WhatsApp</h3>
                <p className="text-gray-600 font-light">
                  Escribinos para consultas rápidas o reservar directamente desde el chat.
                </p>
              </div>
            </a>
          </div>
        </div>
      </section>

      {/* Pase suave de color entre secciones */}
      <div className="h-24 bg-gradient-to-b from-gray-50 to-white"></div>

      {/* Booking Section */}
      <section id="turnos" className="py-32 bg-white text-center">
        <div className="max-w-3xl mx-auto px-6">
          <div className="inline-block p-3 rounded-full bg-black/5 mb-6">
            <Calendar className="h-8 w-8 text-gray-600" />
          </div>

          <h2 className="text-5xl md:text-6xl font-extralight text-black mb-6 tracking-tight">
            Reservá tu turno online
          </h2>

          <p className="text-xl text-gray-600 mb-10 font-light leading-relaxed">
            Accedé a nuestro sistema de reservas y elegí el horario que más te convenga.
          </p>

          <a
            href="https://www.fresha.com/es/a/barba-co-pineyro-avenida-presidente-bernardino-rivadavia-215-o1ukwtm0/all-offer?menu=true&pId=1429418" 
            target="_blank"
            rel="noopener noreferrer"
            className="inline-block bg-black text-white px-12 py-5 rounded-full font-light tracking-wide hover:bg-gray-800 transition-all duration-300"
          >
            Ir a la agenda
          </a>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-black text-white py-16">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          {/* Logo e iconos en una misma línea */}
          <div className="flex justify-between items-center mb-12">
            {/* Logo */}
            <a
              href="#inicio"
              className="flex items-center hover:opacity-80 transition-opacity"
            >
              <img
                src={logo}
                alt="BARBA&CO Logo"
                className="h-10 md:h-12 object-contain"
              />
            </a>


            {/* Iconos */}
            <div className="flex space-x-6">
              <a
                href="https://www.instagram.com/"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-400 hover:text-white transition-colors"
              >
                <Instagram className="h-6 w-6" />
              </a>
              <a
                href="https://wa.me/5491123456789"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-400 hover:text-white transition-colors"
              >
                <Phone className="h-6 w-6" />
              </a>
            </div>
          </div>

          {/* Línea divisoria + texto inferior */}
          <div className="border-t border-gray-800 pt-8 text-center">
            <p className="text-gray-300 font-light text-sm md:text-base">
              © 2025 BARBA&CO — Developed by{" "}
              <a
                href="https://www.instagram.com/nivalis.techlab/"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-200 hover:text-white transition-colors underline underline-offset-2"
              >
                Nivalis
              </a>
            </p>
          </div>
        </div>
      </footer>

    </div>
  );
}

export default App;