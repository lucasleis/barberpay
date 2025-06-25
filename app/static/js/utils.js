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

function mostrarMensajeErrorProducto(mensaje) {
  const messageContainer = document.getElementById('messageContainer');
  if (messageContainer) {
    messageContainer.style.display = 'block';
    messageContainer.textContent = mensaje || 'Debe haber al menos un producto.';
  }
}
function ocultarMensajeErrorProducto() {
  const messageContainer = document.getElementById('messageContainer');
  if (messageContainer) {
    messageContainer.style.display = 'none';
    messageContainer.textContent = '';
  }
}

function agregarProductoRow(currentRow) {
  const newRow = currentRow.cloneNode(true);

  // Asignar nombres a los nuevos campos
  newRow.querySelector('.productSelect').setAttribute('name', 'product_id[]');
  newRow.querySelector('.productCant').setAttribute('name', 'product_quantity[]');

  // Reiniciar valores
  newRow.querySelector('.productSelect').selectedIndex = 0;
  newRow.querySelector('.productCant').selectedIndex = 0;
  newRow.querySelector('.productPrice').value = '';

  // Agregar la nueva fila al DOM
  productSection.appendChild(newRow);

  // Calcular precio y mostrarlo
  const productos = obtenerPrecioProductoRow(newRow);
  insertarValorProductoMostradorRow(newRow, productos.total);

  updatePriceTotal();
}
function eliminarProductoRow(row) {
  const rows = productSection.querySelectorAll('.productRow');

  if (rows.length > 1) {
    row.remove();
    ocultarMensajeErrorProducto();
  } else {
    mostrarMensajeErrorProducto('Debe haber al menos un producto.');
  }

  updatePriceTotal(); 
}

function setValorProducto(){
  // Obtener la primera fila de producto
  const firstRow = document.querySelector('#productSection .productRow');

  if (firstRow) {
    const { total } = obtenerPrecioProductoRow(firstRow);
    insertarValorProductoMostradorRow(firstRow, total);
  }
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

function setValorMembresia() {
  const valorMembresia = obtenerPrecioMembresiaSeleccion();

  const inputPrecio = document.getElementById('membresiaPrice');
  if (inputPrecio) {
    inputPrecio.value = `$${valorMembresia}`;
  }
}

function obtenerPrecioMembresiaSeleccion() {
  const selectedOption = membresiaSelect.options[membresiaSelect.selectedIndex];
  const precio = selectedOption.getAttribute('data-precio');
  return parseFloat(precio) || 0;
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
}

function insertarValorProductoMostrador(precioTotal){  
  const inputPrecio = document.querySelector('.productPrice'); 

  if (inputPrecio) {
    inputPrecio.value = `$${precioTotal}`;
  }

}

function insertarValorProductoMostradorRow(row, precioTotal) {
  const inputPrecio = row.querySelector('.productPrice');

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
        // { fn: ocultarProductSection, toggleId: 'toggleProducto' },
        { fn: ocultarMembresiaSection, toggleId: 'toggleMembresia' },
        { fn: mostrarMembresiaLabel } // Mostrar el label Usa Membresia
      ],
    },
    toggleProducto: {
      show: mostrarProductSection,
      hide: [
        // { fn: ocultarServicioSection, toggleId: 'toggleServicio' },
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

    if (source === 'toggleProducto') {    // inserto valor inicial de cant cuando selecciono el toggle de servicio
      updateCantidadOptions();            // Asumiendo que solo hay un .productSelect en ese momento
      setValorProducto();
      desmarcarPrecioDescuentoAmigo();    // si salgo de servicio desmarco precio descuento y amigo
    }

    if (source === 'toggleMembresia') {   // inserto valor inicial de cant cuando selecciono el toggle de membresia
      setValorMembresia();
      desmarcarPrecioDescuentoAmigo();    // si salgo de servicio desmarco precio descuento y amigo
    }
    ocultarMensajeErrorToggle();
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

function desmarcarPrecioAmigo() {
  const checkbox = document.getElementById('precioAmigoCheckbox');
  if (checkbox.checked) {
    checkbox.checked = false;
  }
}

function desmarcarPrecioDescuento() {
  const checkbox = document.getElementById('precioDescuentoCheckbox');
  if (checkbox.checked) {
    checkbox.checked = false;
  }
}

function desmarcarPrecioDescuentoAmigo() {
  desmarcarPrecioDescuento();
  desmarcarPrecioAmigo();
}

function desmarcarMembresia() {
  const checkbox = document.getElementById('membresiaCheckbox');
  if (checkbox.checked) {
    checkbox.checked = false;
  }
}



/// FUNCIONES NUMERICAS \\\

function formatearMoneda(valor) {
  const numero = Math.round(Number(valor));
  return `$${numero.toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.')}`;
}

function actualizarPrecioServicio() {
  const servicePriceInput = document.getElementById('servicePrice');
  if (!servicePriceInput) return;

  if (checkbox_use_member.checked) {
    servicePriceInput.value = '$0';
    if (amountSimple) amountSimple.value = 0;
    multiPaymentToggle.disabled = false;

  }
}

function obtenerPrecioServicioSeleccion() {
  const usaMembresia = document.getElementById('membresiaCheckbox')?.checked || false;
  const membresiaActivo = membresiaToggle.checked;
  
  // Si está usando un corte de membresía por cualquiera de los dos medios, el precio es 0
  if (membresiaActivo || usaMembresia) {
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

function obtenerPrecioTotalProductosSeleccion() {
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

    // console.log("precio: ",precio, " cantidad: ",cantidad, " total: ",total)
  });

  return { total, items };
}

function obtenerPrecioProductoRow(row) {
  const productSelect = row.querySelector('.productSelect');
  const cantidadSelect = row.querySelector('.productCant');

  if (!productSelect || !cantidadSelect) return { total: 0, item: null };

  const selected = productSelect.options[productSelect.selectedIndex];
  const id = selected.value;
  const precio = parseFloat(selected.getAttribute('data-precio')) || 0;
  const cantidad = parseInt(cantidadSelect.value) || 0;

  if (cantidad > 0) {
    const total = precio * cantidad;
    const item = { id, precio, cantidad };
    return { total, item };
  }

  return { total: 0, item: null };
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
  
  if (membresiaActivo) {

    precioTotal = obtenerPrecioMembresiaSeleccion();
    setValorMembresia();
  
  } else {

    if (servicioActivo) {
      precioTotal += obtenerPrecioServicioSeleccion();    // la funcion valida si se usa membresia
    }

    if (productoActivo) {
      const productosData = obtenerPrecioTotalProductosSeleccion();
      precioTotal += productosData.total;
    }

  }

  updatePrice(); // Aseguramos que el precio del servicio esté actualizado
  
  const tipAmount = parseFloat(document.getElementById('tip').value) || 0;
  const totalConPropina = precioTotal + tipAmount;

  // console.log("updatePriceTotal totalConPropina: ",totalConPropina);

  document.getElementById('totalPago').value = formatearMoneda(totalConPropina);
}



/// FUNCIONES SUBMIT \\\

function mostrarErrorToggle(mostrar) {
  toggleError.style.display = mostrar ? 'block' : 'none';
  toggleContainer.classList.toggle('border', mostrar);
  toggleContainer.classList.toggle('border-danger', mostrar);
  toggleContainer.classList.toggle('rounded', mostrar);
  toggleContainer.classList.toggle('p-2', mostrar);
}
function ocultarMensajeErrorToggle() {
  mostrarErrorToggle(false);
}
function muestraMensajeErrorToggle() {
  mostrarErrorToggle(true);
}

function mostrarErrorMetodoPagoRepetido() {
  const form = document.querySelector('form'); 
  const repeatError = document.getElementById('methodRepeatError');

  if (repeatError) {
    repeatError.style.display = 'block';
  }

  if (form) {
    const metodoInputs = [
      form.querySelector('select[name="method_multiple_1"]'),
      form.querySelector('select[name="method_multiple_2"]')
    ];

    metodoInputs.forEach(select => {
      if (select) {
        select.classList.add('input-error');
      }
    });
  }
}
function ocultarErrorMetodoPagoRepetido() {
  const error = document.getElementById('methodRepeatError');
  if (error) {
    error.style.display = 'none';
  }

  // Quitar clase 'color rojo' de los selects de multiples metodos de pago
  const form = document.querySelector('form'); // o usá un ID específico si lo tenés
  const metodoInputs = [
    form.querySelector('select[name="method_multiple_1"]'),
    form.querySelector('select[name="method_multiple_2"]')
  ];

  metodoInputs.forEach(select => {
    if (select) {
      select.classList.remove('input-error');
    }
  });
}

function mostrarErrorMonto() {
  const montoError = document.getElementById('montoError');
  const form = document.querySelector('form'); 
  const montoInputs = [
    form.querySelector('input[name="amount_method_multi_1"]'),
    form.querySelector('input[name="amount_method_multi_2"]'),
    form.querySelector('input[name="tip"]')
  ];

  if (montoError) {
    montoError.style.display = 'block';
  }

  montoInputs.forEach(input => {
    if (input) {
      input.classList.add('input-error');
    }
  });
}
function ocultarErrorMonto() {
  const montoError = document.getElementById('montoError');
  const form = document.querySelector('form'); 
  const montoInputs = [
    form.querySelector('input[name="amount_method_multi_1"]'),
    form.querySelector('input[name="amount_method_multi_2"]'),
    form.querySelector('input[name="tip"]')
  ];

  if (montoError) {
    montoError.style.display = 'none';
  }

  montoInputs.forEach(input => {
    if (input) {
      input.classList.remove('input-error');
    }
  });
}

function mostrarErrorMembresia() {
  const mensaje = document.getElementById('mensaje_error_membresia');
  const numeroInput = document.getElementById('check_membresia');

  console.log("entra mostrarErrorMembresia");

  if (mensaje) {
    mensaje.style.display = 'block';
  }

  if (numeroInput) {
    numeroInput.classList.add('input-error');
  }
}
function ocultarErrorMembresia() {
  const mensaje = document.getElementById('mensaje_error_membresia');
  const numeroInput = document.getElementById('check_membresia');

  console.log("entra ocultarErrorMembresia");


  if (mensaje) {
    mensaje.style.display = 'none';
  }

  if (numeroInput) {
    numeroInput.classList.remove('input-error');
  }
}




function validarMultiplesMetodos(totalEsperado) {
  const form = document.querySelector('form');

  const amount1 = parseFloat(form.querySelector('input[name="amount_method_multi_1"]').value) || 0;
  const amount2 = parseFloat(form.querySelector('input[name="amount_method_multi_2"]').value) || 0;
  const propina = parseFloat(form.querySelector('input[name="tip"]').value) || 0;
  const totalPagado = amount1 + amount2;

  const method1 = form.querySelector('select[name="method_multiple_1"]').value;
  const method2 = form.querySelector('select[name="method_multiple_2"]').value;

  // Validar métodos repetidos
  if (method1 === method2) {
    mostrarErrorMetodoPagoRepetido();
    return false;
  }

  // Validar cuentas
  if (Math.abs(totalPagado - totalEsperado - propina) > 0.01) {
    mostrarErrorMonto();
    return false;
  }

  return true;
}

function multiplesMetodosValidos(totalEsperado){
  if (multiPaymentToggle.checked && !validarMultiplesMetodos(totalEsperado)) {
    return false;
  }
  return true;
}

function estaSeleccionadaMembresia() {
  const checkbox = document.getElementById('membresiaCheckbox');
  return checkbox.checked;
}




/// MEMBRESIA \\\
function validarSubmitMembresia(){
  const valorMembresia = obtenerPrecioMembresiaSeleccion();
  if (!multiplesMetodosValidos(valorMembresia)) {
    return false;
  }
  return true;
}


/// PRODUCTO \\\
function agregarInputsOcultos(productos) {
  productos.forEach((producto, index) => {
    const inputId = crearInputOculto(`product_id_${index}`, producto.id);
    const inputCant = crearInputOculto(`cantidad_${index}`, producto.cantidad);
    form.appendChild(inputId);
    form.appendChild(inputCant);
  });
}

function validarSubmitProducto() { 
  const productosData = obtenerPrecioTotalProductosSeleccion();

  // console.log("validarSubmitProducto productosData: ",productosData);

  if (productosData.items.length === 0) {                               // valido que no haya cantidad 0
    alert('Debe seleccionar al menos un producto con cantidad válida'); // modificar para que no sea un alert
    return false;
  }

  let productosData_num = String(productosData.total).replace('$', '').replace(/\./g, '');
  productosData_num = parseFloat(productosData_num);

  const totalEsperado = productosData_num;
  // console.log("totalEsperado: ",totalEsperado);

  if (!multiplesMetodosValidos(totalEsperado)) {
    return false;
  }

  return true;
}


/// SERVICIO \\\

function validarSubmitServicio() { 
  //const usa_membresia = document.getElementById('membresiaCheckbox');

  let membresiaValue = parseInt(document.getElementById("check_membresia").value);
  let campo = document.getElementById("check_membresia");
  let mensaje = document.getElementById("mensaje_error_membresia");

  if (estaSeleccionadaMembresia()) {
    if (!membresiaValue) {
      mostrarErrorMembresia();
      return false;
    } 
  } 

  const servicePrecio = obtenerPrecioServicioSeleccion();

  let servicePrecio_num = servicePrecio.toString().replace('$', '').replace(/\./g, '');
  servicePrecio_num = parseFloat(servicePrecio_num);

  const totalEsperado = servicePrecio_num;
  // console.log("totalEsperado: ",totalEsperado);

  if (!multiplesMetodosValidos(totalEsperado)) {
    return false;
  }

  return true;
}


/// SERVICIO Y PRODUCTO \\\

function validarSubmitServicioProducto() { 

  /// Servicio \\\

  let membresiaValue = parseInt(document.getElementById("check_membresia").value);
  
  if (estaSeleccionadaMembresia()) {
    if (!membresiaValue) {
      mostrarErrorMembresia();
      return false;
    } 
  } 

  const servicePrecio = obtenerPrecioServicioSeleccion();

  let servicePrecio_num = servicePrecio.toString().replace('$', '').replace(/\./g, '');
  servicePrecio_num = parseFloat(servicePrecio_num);

  /// Producto \\\

  const productosData = obtenerPrecioTotalProductosSeleccion();

  if (productosData.items.length === 0) {                               // valido que no haya cantidad 0
    alert('Debe seleccionar al menos un producto con cantidad válida'); 
    return false;
  }

  let productosData_num = String(productosData.total).replace('$', '').replace(/\./g, '');
  productosData_num = parseFloat(productosData_num);


  /// Codigo comun a ambos \\\
  const totalEsperado = servicePrecio_num + productosData_num;
  // console.log("totalEsperado: ",totalEsperado);

  if (!multiplesMetodosValidos(totalEsperado)) {
    return false;
  }

  return true;
}

