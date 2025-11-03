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
  Facebook,
  Mail,
  ArrowRight,
  CreditCard,
  DollarSign,
  Check,
  Navigation
} from 'lucide-react';

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

  const testimonials = [
    { 
      name: 'Alexander Chen', 
      rating: 5, 
      text: 'Atención impecable y resultados excepcionales. La experiencia completa supera cualquier expectativa.',
      role: 'CEO, Tech Startup'
    },
    { 
      name: 'Marcus Rodriguez', 
      rating: 5, 
      text: 'Profesionalismo de primer nivel. Cada detalle está cuidadosamente pensado para la excelencia.',
      role: 'Creative Director'
    },
    { 
      name: 'James Morrison', 
      rating: 5, 
      text: 'Un oasis de calma y sofisticación. El servicio personalizado hace toda la diferencia.',
      role: 'Investment Banker'
    }
  ];

  return (
    <div className="min-h-screen bg-white overflow-x-hidden">
      {/* Navigation */}
      <nav className={`fixed w-full z-50 transition-all duration-500 ${
        scrollY > 50 
          ? 'bg-white/95 backdrop-blur-xl shadow-sm border-b border-gray-100' 
          : 'bg-transparent'
      }`}>
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-3">
              <div className="relative">
                <Scissors className={`h-7 w-7 transition-colors duration-300 ${
                  scrollY > 50 ? 'text-black' : 'text-white'
                }`} />
                <div className="absolute -inset-2 bg-gradient-to-r from-gray-600 to-black rounded-full opacity-20 blur-sm"></div>
              </div>
              <span className={`font-light text-xl tracking-wider transition-colors duration-300 ${
                scrollY > 50 ? 'text-black' : 'text-white'
              }`}>
                BARBA&Co
              </span>
            </div>
            
            {/* Desktop Menu */}
            <div className="hidden md:flex space-x-12">
              {['Inicio', 'Servicios', 'Experiencia', 'Contacto'].map((item) => (
                <a 
                  key={item}
                  href={`#${item.toLowerCase()}`} 
                  className={`text-sm font-light tracking-wide transition-all duration-300 hover:opacity-60 relative group ${
                    scrollY > 50 ? 'text-gray-700' : 'text-gray-200'
                  }`}
                >
                  {item}
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
              {['Inicio', 'Servicios', 'Experiencia', 'Contacto'].map((item) => (
                <a 
                  key={item}
                  href={`#${item.toLowerCase()}`} 
                  className="block py-3 text-gray-700 font-light tracking-wide hover:opacity-60 transition-opacity"
                  onClick={() => setIsMenuOpen(false)}
                >
                  {item}
                </a>
              ))}
            </div>
          )}
        </div>
      </nav>

      {/* Hero Section */}
      <section id="inicio" className="relative min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-black to-gray-800">
        <div className="absolute inset-0 bg-black/30"></div>

        {/* Subtle geometric patterns */}
        <div className="absolute inset-0 opacity-5">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 border border-white rounded-full"></div>
          <div className="absolute bottom-1/4 right-1/4 w-64 h-64 border border-white rounded-full"></div>
        </div>

        <div className="relative z-10 text-center px-6 lg:px-8 max-w-5xl mx-auto">
          <div className="mb-8">
            <div className="inline-block p-4 rounded-full bg-white/10 backdrop-blur-sm mb-6">
              <Scissors className="h-12 w-12 text-white" />
            </div>
          </div>

          {/* Nuevo título */}
          <h1 className="text-6xl md:text-8xl font-extralight text-white mb-8 leading-none tracking-tight">
            BARBA<span className="font-thin text-gray-300">&CO</span>
            <span className="block font-thin text-gray-300 text-5xl md:text-7xl mt-2">
              ESTILO Y PRECISIÓN
            </span>
          </h1>

          {/* Nueva frase de bienvenida */}
          <p className="text-xl md:text-2xl text-gray-300 mb-12 max-w-3xl mx-auto font-light leading-relaxed">
            Tu barbería en Avellaneda. Donde el estilo se perfecciona con técnica, precisión y pasión.
          </p>

          <div className="flex flex-col sm:flex-row gap-6 justify-center items-center">
            <button className="group bg-white text-black px-10 py-4 rounded-full font-light tracking-wide hover:bg-gray-100 transition-all duration-300 transform hover:scale-105 flex items-center space-x-2">
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


      {/* Experience Section */}
      <section id="experiencia" className="py-32 bg-white">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-20 items-center">
            <div>
              <div className="inline-block p-3 rounded-full bg-black/5 mb-8">
                <Star className="h-8 w-8 text-gray-600" />
              </div>
              
              <h2 className="text-5xl md:text-6xl font-extralight text-black mb-8 tracking-tight leading-tight">
                Más que una
                <span className="block">barbería</span>
              </h2>
              
              <p className="text-xl text-gray-600 mb-8 font-light leading-relaxed">
                Creamos experiencias memorables donde la tradición artesanal se encuentra 
                con la innovación moderna. Cada visita es un momento de relajación y 
                transformación personal.
              </p>
              
              <div className="space-y-6">
                {[
                  'Consulta personalizada de estilo',
                  'Productos premium seleccionados',
                  'Ambiente relajante y sofisticado',
                  'Atención al detalle excepcional'
                ].map((feature, index) => (
                  <div key={index} className="flex items-center space-x-4">
                    <div className="w-6 h-6 rounded-full bg-black/10 flex items-center justify-center">
                      <Check className="h-3 w-3 text-gray-600" />
                    </div>
                    <span className="text-gray-700 font-light">{feature}</span>
                  </div>
                ))}
              </div>
              
              <div className="grid grid-cols-3 gap-8 mt-12 pt-8 border-t border-gray-100">
                <div className="text-center">
                  <div className="text-4xl font-extralight text-black mb-2">15+</div>
                  <div className="text-gray-500 text-sm font-light tracking-wide">Años</div>
                </div>
                <div className="text-center">
                  <div className="text-4xl font-extralight text-black mb-2">2.5K+</div>
                  <div className="text-gray-500 text-sm font-light tracking-wide">Clientes</div>
                </div>
                <div className="text-center">
                  <div className="text-4xl font-extralight text-black mb-2">98%</div>
                  <div className="text-gray-500 text-sm font-light tracking-wide">Satisfacción</div>
                </div>
              </div>
            </div>
            
            <div className="relative">
              <div className="bg-gradient-to-br from-gray-100 to-gray-200 h-96 lg:h-[500px] rounded-3xl flex items-center justify-center relative overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-br from-black/5 to-transparent"></div>
                <Scissors className="h-24 w-24 text-gray-400" />
              </div>
              
              {/* Floating elements */}
              <div className="absolute -top-6 -right-6 w-24 h-24 bg-white rounded-2xl shadow-lg flex items-center justify-center">
                <Star className="h-8 w-8 text-gray-600" />
              </div>
              <div className="absolute -bottom-6 -left-6 w-32 h-20 bg-black rounded-2xl flex items-center justify-center">
                <span className="text-white font-light text-sm tracking-wider">PREMIUM</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Location Section */}
      <section id="ubicación" className="py-32 bg-white">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-20 items-center">
            <div>
              <div className="inline-block p-3 rounded-full bg-black/5 mb-8">
                <MapPin className="h-8 w-8 text-gray-600" />
              </div>
              
              <h2 className="text-5xl md:text-6xl font-extralight text-black mb-8 tracking-tight leading-tight">
                Encuéntranos
              </h2>
              
              <p className="text-xl text-gray-600 mb-8 font-light leading-relaxed">
                Ubicados en el corazón de Avellaneda, nuestro atelier es fácilmente accesible 
                desde cualquier punto de la ciudad. Un espacio diseñado para tu comodidad 
                y conveniencia.
              </p>
              
              <div className="bg-gray-50 p-8 rounded-3xl mb-8">
                <h3 className="text-2xl font-light text-black mb-6 tracking-wide">Dirección</h3>
                <p className="text-lg text-gray-700 font-light mb-4">
                  Av. Presidente Masaryk 456<br />
                  Avellaneda V Sección<br />
                  11560 Ciudad de México, CDMX
                </p>
                <button className="flex items-center space-x-2 text-black hover:opacity-60 transition-opacity">
                  <Navigation className="h-4 w-4" />
                  <span className="text-sm font-light tracking-wide">Ver en Google Maps</span>
                </button>
              </div>
              
              <div className="space-y-6">
                {[
                  { icon: MapPin, text: 'Zona segura y céntrica' },
                  { icon: Clock, text: 'Fácil acceso en horarios laborales' }
                ].map((feature, index) => {
                  const Icon = feature.icon;  // ✅ definir el componente
                  return (
                    <div key={index} className="flex items-center space-x-4">
                      <div className="w-10 h-10 rounded-2xl bg-black/5 flex items-center justify-center">
                        <Icon className="h-4 w-4 text-gray-600" />  {/* ✅ usar el componente */}
                      </div>
                      <span className="text-gray-700 font-light">{feature.text}</span>
                    </div>
                  );
                })}
              </div>
              
              <div className="grid grid-cols-2 gap-8 mt-12 pt-8 border-t border-gray-100">
                <div>
                  <div className="text-3xl font-extralight text-black mb-2">5 min</div>
                  <div className="text-gray-500 text-sm font-light tracking-wide">Desde Reforma</div>
                </div>
                <div>
                  <div className="text-3xl font-extralight text-black mb-2">2 min</div>
                  <div className="text-gray-500 text-sm font-light tracking-wide">Desde Antara</div>
                </div>
              </div>
            </div>
            
            <div className="relative">
              <div className="bg-gradient-to-br from-gray-100 to-gray-200 h-96 lg:h-[500px] rounded-3xl relative overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-br from-black/5 to-transparent"></div>
                
                {/* Mapa simulado */}
                <div className="absolute inset-4 bg-white rounded-2xl shadow-inner flex items-center justify-center">
                  <div className="text-center">
                    <MapPin className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-500 font-light text-sm">Mapa Interactivo</p>
                    <p className="text-gray-400 font-light text-xs mt-1">Click para abrir</p>
                  </div>
                </div>
                
                {/* Puntos de referencia */}
                <div className="absolute top-8 left-8 bg-black/80 backdrop-blur-sm text-white px-3 py-2 rounded-xl text-xs font-light">
                  Avellaneda
                </div>
                <div className="absolute bottom-8 right-8 bg-white/90 backdrop-blur-sm text-black px-3 py-2 rounded-xl text-xs font-light">
                  Metro Avellaneda
                </div>
              </div>
              
              {/* Floating elements */}
              <div className="absolute -top-6 -right-6 w-24 h-24 bg-white rounded-2xl shadow-lg flex items-center justify-center">
                <Navigation className="h-8 w-8 text-gray-600" />
              </div>
              <div className="absolute -bottom-6 -left-6 w-32 h-20 bg-black rounded-2xl flex items-center justify-center">
                <span className="text-white font-light text-sm tracking-wider">Avellaneda</span>
              </div>
            </div>
          </div>
        </div>
      </section>


      {/* Testimonials */}
      <section className="py-32 bg-gray-900">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="text-center mb-20">
            <div className="inline-block p-3 rounded-full bg-white/10 mb-6">
              <Star className="h-8 w-8 text-white" />
            </div>
            <h2 className="text-5xl md:text-6xl font-extralight text-white mb-6 tracking-tight">
              Testimonios
            </h2>
            <p className="text-xl text-gray-300 max-w-2xl mx-auto font-light">
              La opinión de nuestros clientes es nuestro mayor reconocimiento
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <div key={index} className="bg-gray-800/50 backdrop-blur-sm p-8 rounded-3xl border border-gray-700/50 hover:bg-gray-800/70 transition-all duration-300">
                <div className="flex mb-6">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <Star key={i} className="h-4 w-4 text-white fill-current" />
                  ))}
                </div>
                
                <p className="text-gray-300 mb-6 font-light leading-relaxed italic">
                  "{testimonial.text}"
                </p>
                
                <div className="border-t border-gray-700 pt-6">
                  <p className="text-white font-light text-lg">{testimonial.name}</p>
                  <p className="text-gray-400 text-sm font-light">{testimonial.role}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Contact Section */}
      <section id="contacto" className="py-32 bg-white">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-20">
            <div>
              <div className="inline-block p-3 rounded-full bg-black/5 mb-8">
                <MapPin className="h-8 w-8 text-gray-600" />
              </div>
              
              <h2 className="text-5xl md:text-6xl font-extralight text-black mb-8 tracking-tight">
                Visítanos
              </h2>
              
              <div className="space-y-8">
                <div className="flex items-start space-x-6">
                  <div className="w-12 h-12 rounded-2xl bg-gray-100 flex items-center justify-center flex-shrink-0">
                    <MapPin className="h-5 w-5 text-gray-600" />
                  </div>
                  <div>
                    <p className="font-light text-black text-lg mb-1">Ubicación</p>
                    <p className="text-gray-600 font-light">Av. Reforma 456, Avellaneda<br />Ciudad de México</p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-6">
                  <div className="w-12 h-12 rounded-2xl bg-gray-100 flex items-center justify-center flex-shrink-0">
                    <Phone className="h-5 w-5 text-gray-600" />
                  </div>
                  <div>
                    <p className="font-light text-black text-lg mb-1">Contacto</p>
                    <p className="text-gray-600 font-light">+52 55 1234 5678</p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-6">
                  <div className="w-12 h-12 rounded-2xl bg-gray-100 flex items-center justify-center flex-shrink-0">
                    <Clock className="h-5 w-5 text-gray-600" />
                  </div>
                  <div>
                    <p className="font-light text-black text-lg mb-1">Horarios</p>
                    <p className="text-gray-600 font-light">
                      Lunes - Viernes: 10:00 - 20:00<br />
                      Sábado: 9:00 - 19:00<br />
                      Domingo: Cerrado
                    </p>
                  </div>
                </div>
              </div>

              <div className="mt-12 pt-8 border-t border-gray-100">
                <p className="text-gray-500 font-light mb-6">Síguenos</p>
                <div className="flex space-x-4">
                  <div className="w-12 h-12 rounded-2xl bg-gray-100 flex items-center justify-center hover:bg-gray-200 transition-colors cursor-pointer">
                    <Instagram className="h-5 w-5 text-gray-600" />
                  </div>
                  <div className="w-12 h-12 rounded-2xl bg-gray-100 flex items-center justify-center hover:bg-gray-200 transition-colors cursor-pointer">
                    <Facebook className="h-5 w-5 text-gray-600" />
                  </div>
                  <div className="w-12 h-12 rounded-2xl bg-gray-100 flex items-center justify-center hover:bg-gray-200 transition-colors cursor-pointer">
                    <Mail className="h-5 w-5 text-gray-600" />
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-gray-50 p-10 rounded-3xl">
              <h3 className="text-3xl font-light text-black mb-8 tracking-wide">
                Reserva tu cita
              </h3>
              
              <form className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <input 
                    type="text" 
                    placeholder="Nombre" 
                    className="w-full p-4 bg-white border border-gray-200 rounded-2xl focus:outline-none focus:border-gray-400 transition-colors font-light"
                  />
                  <input 
                    type="tel" 
                    placeholder="Teléfono" 
                    className="w-full p-4 bg-white border border-gray-200 rounded-2xl focus:outline-none focus:border-gray-400 transition-colors font-light"
                  />
                </div>
                
                <select className="w-full p-4 bg-white border border-gray-200 rounded-2xl focus:outline-none focus:border-gray-400 transition-colors font-light">
                  <option>Selecciona un servicio</option>
                  {services.map((service, index) => (
                    <option key={index}>{service.name}</option>
                  ))}
                </select>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <input 
                    type="date" 
                    className="w-full p-4 bg-white border border-gray-200 rounded-2xl focus:outline-none focus:border-gray-400 transition-colors font-light"
                  />
                  <input 
                    type="time" 
                    className="w-full p-4 bg-white border border-gray-200 rounded-2xl focus:outline-none focus:border-gray-400 transition-colors font-light"
                  />
                </div>
                
                <textarea 
                  placeholder="Notas adicionales (opcional)"
                  rows={4}
                  className="w-full p-4 bg-white border border-gray-200 rounded-2xl focus:outline-none focus:border-gray-400 transition-colors font-light resize-none"
                ></textarea>
                
                <button className="w-full bg-black text-white py-4 rounded-2xl font-light tracking-wide hover:bg-gray-800 transition-colors duration-300 flex items-center justify-center space-x-2">
                  <span>Confirmar Reserva</span>
                  <ArrowRight className="h-4 w-4" />
                </button>
              </form>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-black text-white py-16">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center space-x-3 mb-8 md:mb-0">
              <Scissors className="h-8 w-8 text-white" />
              <span className="font-light text-xl tracking-wider">BARBA&CO</span>
            </div>
            
            <div className="flex space-x-12 mb-8 md:mb-0">
              {['Inicio', 'Servicios', 'Experiencia', 'Contacto'].map((item) => (
                <a 
                  key={item}
                  href={`#${item.toLowerCase()}`} 
                  className="text-gray-400 hover:text-white transition-colors font-light tracking-wide"
                >
                  {item}
                </a>
              ))}
            </div>
            
            <div className="text-gray-500 text-sm font-light">
              © 2025 Nivalis
            </div>
          </div>
          
          <div className="border-t border-gray-800 mt-12 pt-8 text-center">
            <p className="text-gray-500 font-light text-sm">
              Crafted with precision and passion
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;