// utils.js

// Funciones Genericas 

function ocultarElemento(id) {
  const el = document.getElementById(id);
  if (el) el.style.display = 'none';
}

function mostrarElemento(id) {
  const el = document.getElementById(id);
  if (el) el.style.display = 'block';
}

function toggleActivado(idToggle) {
  const toggle = document.getElementById(idToggle);
  return toggle ? toggle.checked : false;
}

function desactivarToggle(idToggle) {
  const toggle = document.getElementById(idToggle);
  if (toggle) toggle.checked = false;
}

function setRequired(selector) {
  const container = document.querySelector(selector);
  if (container) {
    container.querySelectorAll('input').forEach(el => el.required = true);
  }
}

function quitarRequired(selector) {
  const container = document.querySelector(selector);
  if (container) {
    container.querySelectorAll('input').forEach(el => el.required = false);
  }
}



/// SERVICIOS \\\

function ocultarServicioSection() {
  ocultarElemento('servicioSection');
}
function mostrarServicioSection() {
  mostrarElemento('servicioSection');
}

function mostrarLabelPrecioDesc() {
  mostrarElemento('labelPrecioDesc');
}
function ocultarLabelPrecioDesc() {
  ocultarElemento('labelPrecioDesc');
}

function mostrarLabelPrecioAmigo() {
  mostrarElemento('labelPrecioAmigo');
}
function ocultarLabelPrecioAmigo() {
  ocultarElemento('labelPrecioAmigo');
}




/// PRODUCTOS \\\

function ocultarProductSection() {
  ocultarElemento('productSection');
}
function mostrarProductSection() {
  mostrarElemento('productSection');
}



/// MEMBRESIAS \\\
function ocultarMembresiaSection() {
  ocultarElemento('membresiaSection');
}
function mostrarMembresiaSection() {
  mostrarElemento('membresiaSection');
}

function mostrarMembresiaInput() {
  mostrarElemento('membresiaMethodGroup');
}
function ocultarMembresiaInput() {
  ocultarElemento('membresiaMethodGroup');
}



/// METODOS DE PAGO \\\

function mostrarMetodoPago() {
  mostrarElemento('divMetodoPago');
  // mostrarPagoSimpleGroup();
}
function ocultarMetodoPago() {
  ocultarElemento('divMetodoPago');
  // ocultarPagoSimpleGroup();
  // ocultarMultiPagosGroup();
}

function mostrarMembresiaLabel() {
  mostrarElemento('membresiaLabel');
}
function ocultarMembresiaLabel() {
  ocultarElemento('membresiaLabel');
}

function mostrarMultiPagosCheckbox() {
  mostrarElemento('MultiPagosLabel');
}
function ocultarMultiPagosCheckbox() {
  ocultarElemento('MultiPagosLabel');
}

function mostrarPagoSimpleGroup() {
  mostrarElemento('singleMethodGroup');
}
function ocultarPagoSimpleGroup() {
  ocultarElemento('singleMethodGroup');
}

function mostrarMultiPagosGroup() {
  mostrarElemento('multiMethodGroup');
}
function ocultarMultiPagosGroup() {
  ocultarElemento('multiMethodGroup');
}


// Actualiza las opciones de cantidad según el producto seleccionado
function updateCantidadOptions() {
  const selectElement = document.querySelector('.productSelect');
  if (!selectElement) return;

  const row = selectElement.closest('.productRow');
  const selectedOption = selectElement.options[selectElement.selectedIndex];
  const cantidadDisponible = parseInt(selectedOption.dataset.cantidad || 0);

  const cantidadSelect = row.querySelector('.productCant');
  cantidadSelect.innerHTML = ''; // Limpiar opciones previas

  const maxCantidad = Math.min(10, cantidadDisponible);

  for (let i = 1; i <= maxCantidad; i++) {
    const option = document.createElement('option');
    option.value = i;
    option.textContent = i;
    cantidadSelect.appendChild(option);
  }

    // updatePrice(row); // Actualizar el precio si querés
}

function insertarValorProductoMostrador(precioTotal){     // verificar que no este obteniendo el valor de TODOS los productos en carrito
  const inputPrecio = document.querySelector('.productPrice'); 

  if (inputPrecio) {
    inputPrecio.value = `$${precioTotal}`;
  }

}



// Funciones de script \\\

function resetTip() {
  const tipInput = document.getElementById('tip');
  tipInput.value = 0;
  updatePriceTotal(); // Actualiza el total sin la propina
}

function activarMetodoPagoMultiple() {
  ocultarPagoSimpleGroup();
  mostrarMultiPagosGroup();
  setRequired('multiMethodGroup');
  // paymentMethodsGroup.classList.add('multiple');
}

function desactivarMetodoPagoMultiple() {
  mostrarPagoSimpleGroup();
  ocultarMultiPagosGroup();

  quitarRequired('multiMethodGroup');
  // errorMultiplesPagos.style.display = 'none';
  // repeatError.style.display = 'none';
  // paymentMethodsGroup.classList.remove('multiple');
}

function updateToggleSections(e = null) {
  const source = e?.target?.id || null;

  const config = {
    toggleMembresia: {
      show: mostrarMembresiaSection,
      hide: [
        { fn: ocultarServicioSection, toggleId: 'toggleServicio' },
        { fn: ocultarProductSection, toggleId: 'toggleProducto' },
        { fn: ocultarMembresiaLabel } // Ocultar el label Usa Membresia
      ],
    },
    toggleServicio: {
      show: mostrarServicioSection,
      hide: [
        { fn: ocultarProductSection, toggleId: 'toggleProducto' },
        { fn: ocultarMembresiaSection, toggleId: 'toggleMembresia' },
        { fn: mostrarMembresiaLabel } // Mostrar el label Usa Membresia

      ],
    },
    toggleProducto: {
      show: mostrarProductSection,
      hide: [
        { fn: ocultarServicioSection, toggleId: 'toggleServicio' },
        { fn: ocultarMembresiaSection, toggleId: 'toggleMembresia' },
        { fn: ocultarMembresiaLabel } // Ocultar el label Usa Membresia

      ],
    }
  };

  // Mostrar la sección correspondiente y ocultar las otras
  if (source && toggleActivado(source) && config[source]) {
    config[source].show();

    config[source].hide.forEach(({ fn, toggleId }) => {
      fn();
      desactivarToggle(toggleId);
    });

    // desactivar cualquier posible boton
    desactivarMetodoPagoMultiple();
    ocultarMembresiaInput();
    membresiaCheckbox.checked = false;    // saco seleccion a checkbox de membresia
    mostrarPagoSimpleGroup();
    multiPaymentToggle.checked = false;   // saco seleccion a checkbox de multiples pagos

    mostrarMetodoPago();

    if (source === 'toggleProducto') {  // inserto valor inicial de cant cuando selecciono el toggle de servicio
      updateCantidadOptions();          // Asumiendo que solo hay un .productSelect en ese momento
    }
  }

  // Si todos están desactivados, ocultar todo
  const ningunoActivo = !toggleActivado('toggleMembresia') &&
                        !toggleActivado('toggleServicio') &&
                        !toggleActivado('toggleProducto');

  if (ningunoActivo) {
    ocultarMembresiaSection();
    ocultarServicioSection();
    ocultarProductSection();
    ocultarMetodoPago();
  }


  resetTip(); // hace updatePriceTotal(); dentro de reset
}




/// FUNCIONES NUMERICAS \\\

function formatearMoneda(valor) {
  const numero = Math.round(Number(valor));
  return `$${numero.toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.')}`;
}


function obtenerPrecioMembresiaSeleccion() {
  const input = document.getElementById('membreciaPrice');
  const valor = input.value.replace(/\./g, '').replace('$', '').trim();
  return parseFloat(valor) || 0;
}

function obtenerPrecioProductosSeleccion() {
  const rows = document.querySelectorAll('#productSection .productRow');
  const items = [];
  let total = 0;

  rows.forEach((row) => {
    const productSelect = row.querySelector('.productSelect');
    const cantidadSelect = row.querySelector('.productCant');

    if (!productSelect || !cantidadSelect) return;

    const selected = productSelect.options[productSelect.selectedIndex];
    const id = selected.value;
    const precio = parseFloat(selected.getAttribute('data-precio')) || 0;
    const cantidad = parseInt(cantidadSelect.value) || 0;

    if (cantidad > 0) {
      items.push({ id, precio, cantidad });
      total += precio * cantidad;
    }

    console.log("precio: ",precio, " cantidad: ",cantidad, " total: ",total)

  });

  return { total, items };
}

function obtenerPrecioServicioSeleccion() {
  const usaMembresia = document.getElementById('membresiaCheckbox')?.checked || false;
  const membresiaActivo = membresiaToggle.checked;

  // Si está usando un corte de membresía, el precio es 0
  if (membresiaActivo && usaMembresia) {
    return 0;
  }

  const selected = serviceSelect.options[serviceSelect.selectedIndex];
  if (!selected) return 0;

  if (precioDescuentoCheckbox.checked) {
    return parseFloat(selected.getAttribute('data-precio-descuento')) || 0;
  } else if (precioAmigoCheckbox.checked) {
    return parseFloat(selected.getAttribute('data-precio-amigo')) || 0;
  }

  return parseFloat(selected.getAttribute('data-precio')) || 0;
}


function updatePrice() {
  const precio = obtenerPrecioServicioSeleccion();
  const precioRedondeado = Math.round(precio);

  // Formatear con separador de miles y símbolo $
  const precioFormateado = formatearMoneda(precio);

  // Asignar valores al input visible y al oculto
  servicePrice.value = precioFormateado;
  amountSimple.value = precioRedondeado; // Este mantiene el valor numérico sin formato
}

function updatePriceTotal() {
  let precioTotal = 0;

  const servicioActivo = servicioToggle.checked;
  const productoActivo = productoToggle.checked;
  const membresiaActivo = membresiaToggle.checked;
  // const usaMembresia = document.getElementById('membresiaCheckbox')?.checked || false;
  
  if (membresiaActivo) {
    
    precioTotal = obtenerPrecioMembresiaSeleccion();
    console.log("membresiaActivo precioTotal: ",precioTotal);
  
  } else {

    if (servicioActivo) {
      precioTotal += obtenerPrecioServicioSeleccion();    // la funcion valida si se usa membrecia
      console.log("servicioActivo precioTotal: ",precioTotal);
    }

    if (productoActivo) {
      const productosData = obtenerPrecioProductosSeleccion();
      precioTotal += productosData.total;
      // console.log("productoActivo precioTotal: ",precioTotal);
      insertarValorProductoMostrador(precioTotal)
    }
  }

  updatePrice(); // Aseguramos que el precio del servicio esté actualizado
  
  const tipAmount = parseFloat(document.getElementById('tip').value) || 0;
  const totalConPropina = precioTotal + tipAmount;

  document.getElementById('totalPago').value = formatearMoneda(totalConPropina);
}
