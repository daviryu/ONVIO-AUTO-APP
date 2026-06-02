from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import os
from logger_config import logger, config

def navigate_to_boletos(driver, wait):
    try:
        logger.info(
            "Aguardando árvore de pastas carregar..."
        )


        logger.info(
            "Procurando pasta Financeiro..."
        )

        # Procura a linha Financeiro na tabela principal
        financeiro = wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//a[contains(text(),'Financeiro')]"
                )
            )
        )

        driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            financeiro
        )

        time.sleep(0.5)

        driver.execute_script(
            "arguments[0].click();",
            financeiro
        )

        logger.info(
            "Pasta Financeiro clicada."
        )

        time.sleep(0.5)


        logger.info(
            "Procurando pasta Boletos..."
        )

        boletos = wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//a[contains(text(),'Boletos')]"
                )
            )
        )

        driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            boletos
        )

        time.sleep(1)

        driver.execute_script(
            "arguments[0].click();",
            boletos
        )

        logger.info(
            "Pasta Boletos selecionada."
        )

        time.sleep(1)

        return True

    except Exception as e:

        logger.error(
            f"Erro ao navegar para Boletos: {e}"
        )
        
        return False

def open_documentos_page(driver, wait):

    try:
        logger.info(
            "Verificando página de Documentos..."
        )

        try:
            wait.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//a[contains(., 'Documentos') "
                        "and (contains(@class,'active') "
                        "or @aria-current='page')]"
                    )
                )
            )

            logger.info(
                "Página de Documentos já aberta."
            )

            return True

        except Exception:
            logger.info(
                "Página Documentos ainda não aberta."
            )

        logger.info(
            "Clicando em 'Documentos'..."
        )

        documentos_btn = wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//a[contains(., 'Documentos')]"
                )
            )
        )

        driver.execute_script(
            "arguments[0].click();",
            documentos_btn
        )

        logger.info(
            "Botão 'Documentos' clicado."
        )

        time.sleep(1)

        return True

    except Exception as e:

        logger.error(
            f"Erro ao abrir Documentos: {e}"
        )

        return False

def run_onvio_upload(file_path, new_name, due_date, client_code):
    logger.info(f"Iniciando upload para o cliente {client_code} com o arquivo {os.path.basename(file_path)}")
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{config['chrome_debug_port']}")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.maximize_window() 
        wait = WebDriverWait(driver, 30) # Aumentado o tempo de espera
        
        # 1. Localizar aba ONVIO de forma rápida
        if "onvio.com.br" not in driver.current_url:
            found_onvio_tab = False
            for handle in driver.window_handles:
                driver.switch_to.window(handle)
                if "onvio.com.br" in driver.current_url:
                    found_onvio_tab = True
                    logger.info("Aba do ONVIO encontrada e selecionada.")
                    break
            if not found_onvio_tab:
                logger.error("Nenhuma aba do ONVIO foi encontrada no navegador. Certifique-se de que o ONVIO está aberto.")
                return False, "Nenhuma aba do ONVIO encontrada."
        # Abrir Documentos automaticamente
        if not open_documentos_page(driver, wait):

            logger.error(
                "Falha ao abrir a página Documentos."
            )

            return False, "Erro ao abrir Documentos."

        
        # 2. Busca de Cliente
        logger.info(
            f"Buscando cliente com código: {client_code}"
        )

        try:

            search_input = wait.until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//input[contains(@aria-label,'Cliente') "
                        "or contains(@placeholder,'Cliente') "
                        "or contains(@placeholder,'cliente')]"
                    )
                )
            )

            # clica no campo
            driver.execute_script(
                "arguments[0].click();",
                search_input
            )

            time.sleep(0.5)

            # limpa completamente
            search_input.send_keys(
                Keys.CONTROL,
                "a"
            )

            search_input.send_keys(
                Keys.DELETE
            )

            time.sleep(0.3)

            # digita código
            search_input.send_keys(
                str(client_code)
            )

            logger.info(
                f"Código '{client_code}' digitado."
            )

            # espera dropdown carregar
            # NÃO ALTERAR ESSE TIME.SLEEP
            time.sleep(2)
            # NÃO ALTERAR ESSE TIME.SLEEP

            logger.info(
                "Confirmando cliente com ENTER..."
            )

            # apenas ENTER
            search_input.send_keys(
                Keys.ENTER
            )

            logger.info(
                "ENTER enviado."
            )

            # aguarda página trocar
            time.sleep(2)

            logger.info(
                "Aguardando árvore do novo cliente..."
            )

            wait.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//*[contains(text(),'Financeiro')]"
                    )
                )
            )

            logger.info(
                f"Cliente {client_code} carregado."
            )

            # abrir Financeiro > Boletos
            if not navigate_to_boletos(
                driver,
                wait
            ):

                logger.error(
                    "Falha ao acessar Financeiro > Boletos."
                )

                return False, (
                    "Erro ao abrir pasta Boletos."
                )

        except Exception as e:

            logger.error(
                f"Erro na busca do cliente: {e}"
            )

            return False, (
                "Erro na busca do cliente."
            )

        # ==========================
        # 3. UPLOAD DO ARQUIVO
        # ==========================

        logger.info(
            f"Iniciando upload do arquivo: "
            f"{os.path.basename(file_path)}"
        )

        try:

            time.sleep(1)

            upload_btn = wait.until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        (
                            "//button[contains(., 'Upload')]"
                            " | //a[contains(., 'Upload')]"
                        )
                    )
                )
            )

            driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});",
                upload_btn
            )

            time.sleep(0.5)

            driver.execute_script(
                "arguments[0].click();",
                upload_btn
            )

            logger.info(
                "Botão Upload clicado."
            )

            time.sleep(1)

            # procura TODOS os inputs file
            file_inputs = driver.find_elements(
                By.XPATH,
                "//input[@type='file']"
            )

            logger.info(
                f"Inputs file encontrados: "
                f"{len(file_inputs)}"
            )

            if not file_inputs:
                raise Exception(
                    "Nenhum input file encontrado."
                )

            # pega o último (geralmente é o do modal recém aberto)
            file_input = file_inputs[-1]

            abs_path = os.path.abspath(file_path)

            logger.info(
                f"Enviando arquivo: {abs_path}"
            )

            # conta documentos antes do upload
            qtd_antes = len(
                driver.find_elements(
                    By.XPATH,
                    "//div[contains(@class,'wj-row')]"
                )
            )

            logger.info(
                f"Documentos antes do upload: "
                f"{qtd_antes}"
            )

            file_input.send_keys(abs_path)

            logger.info(
                f"Arquivo enviado: "
                f"{os.path.basename(file_path)}"
            )

            logger.info(
                "Aguardando upload finalizar..."
            )

            time.sleep(4)

        except Exception as e:

            logger.error(
                f"Erro durante upload: {e}"
            )

            return False, (
                "Erro no upload do arquivo."
            )


        # ==========================================
        # AGUARDAR DOCUMENTO APARECER
        # ==========================================

        logger.info(
            "Aguardando documento aparecer..."
        )

        try:

            file_name = os.path.basename(
                file_path
            )

            timeout = 90
            inicio = time.time()

            while time.time() - inicio < timeout:

                documentos = driver.find_elements(
                    By.XPATH,
                    f"//a[contains(text(), '{file_name}')]"
                )

                visivel = False

                for doc in documentos:
                    try:
                        if doc.is_displayed():
                            visivel = True
                            break
                    except:
                        pass

                if visivel:

                    logger.info(
                        "Documento apareceu na lista."
                    )

                    break

                logger.info(
                    "Documento ainda não apareceu..."
                )

                time.sleep(2)

            else:
                raise Exception(
                    "Documento não apareceu."
                )

        except Exception as e:

            logger.error(
                f"Documento não apareceu: {e}"
            )

            return False, (
                "Upload aparentemente falhou "
                "ou documento não carregou."
            )

            time.sleep(2)

        # ==========================================
        # FUNÇÃO PARA SELECIONAR CHECKBOX
        # ==========================================

        from selenium.webdriver.common.action_chains import ActionChains

        def selecionar_documento():

            try:

                file_name = os.path.basename(
                    file_path
                )

                # localizar TODOS os documentos com o nome
                documentos = driver.find_elements(
                    By.XPATH,
                    f"//a[contains(text(), '{file_name}')]"
                )

                if not documentos:
                    raise Exception(
                        "Documento não encontrado."
                    )

                documento = None

                # pegar somente o que está realmente visível
                for doc in documentos:

                    try:
                        if doc.is_displayed():

                            rect = driver.execute_script("""
                                const r =
                                    arguments[0]
                                    .getBoundingClientRect();

                                return {
                                    top: r.top,
                                    bottom: r.bottom
                                };
                            """, doc)

                            # ignorar elementos fora da tela
                            if rect["top"] > 0:

                                documento = doc
                                break

                    except:
                        pass

                if documento is None:
                    raise Exception(
                        "Documento visível não encontrado."
                    )

                logger.info(
                    "Documento localizado na lista."
                )

                # pegar posição do documento na tela
                doc_rect = driver.execute_script("""
                    const r =
                        arguments[0]
                        .getBoundingClientRect();

                    return {
                        top: r.top,
                        left: r.left,
                        height: r.height
                    };
                """, documento)

                logger.info(
                    f"Documento em Y="
                    f"{doc_rect['top']}"
                )

                # garantir documento visível
                driver.execute_script("""
                    arguments[0].scrollIntoView({
                        block: 'center',
                        inline: 'nearest'
                    });
                """, documento)

                time.sleep(1)

                logger.info(
                    "Documento trazido para área visível."
                )

                # pegar posição REAL do documento
                doc_rect = driver.execute_script("""
                    const r = arguments[0]
                        .getBoundingClientRect();

                    return {
                        left: r.left,
                        top: r.top,
                        width: r.width,
                        height: r.height
                    };
                """, documento)

                logger.info(
                    f"Documento localizado em "
                    f"X={doc_rect['left']} "
                    f"Y={doc_rect['top']}"
                )

                # coordenadas reais da checkbox
                # baseadas na régua do DevTools
                click_x = 360
                click_y = (
                    doc_rect["top"] +
                    (doc_rect["height"] / 2)
                )

                logger.info(
                    f"Clique checkbox FIXO em "
                    f"X={click_x}, "
                    f"Y={click_y}"
                )

                # pega elemento EXATO nessa posição
                driver.execute_script("""
                    const x = arguments[0];
                    const y = arguments[1];

                    const el = document.elementFromPoint(x, y);

                    if(el){
                        el.dispatchEvent(
                            new MouseEvent('mousedown', {
                                bubbles: true
                            })
                        );

                        el.dispatchEvent(
                            new MouseEvent('mouseup', {
                                bubbles: true
                            })
                        );

                        el.click();
                    }
                """, click_x, click_y)

                logger.info(
                    "Checkbox clicada."
                )

                time.sleep(1)

                return True

            except Exception as e:

                logger.error(
                    f"Erro ao selecionar documento: {e}"
                )

                return False

        # ==========================================
        # SELECIONAR DOCUMENTO
        # ==========================================

        logger.info(
            "Selecionando documento enviado..."
        )

        if not selecionar_documento():

            return False, (
                "Erro ao selecionar documento."
            )

        logger.info(
            "Documento selecionado."
        )


        # ==========================================
        # RENOMEAR DOCUMENTO
        # ==========================================

        logger.info(
            "Iniciando renomeação..."
        )

        try:

            logger.info(
                "Localizando botão Gerenciar..."
            )

            gerenciar = wait.until(
                EC.presence_of_element_located(
                    (
                        By.ID,
                        "dms-fe-legacy-components-client-documents-manage-docs-menu-button"
                    )
                )
            )

            logger.info(
                "Botão Gerenciar localizado."
            )

            # garantir visibilidade
            driver.execute_script("""
                arguments[0].scrollIntoView({
                    block:'center'
                });
            """, gerenciar)

            time.sleep(0.5)

            logger.info(
                "Clicando em Gerenciar..."
            )

            # clique JS funciona melhor no Angular
            driver.execute_script(
                "arguments[0].click();",
                gerenciar
            )

            logger.info(
                "Botão Gerenciar clicado."
            )

            time.sleep(1)

            logger.info(
                "Procurando botão Renomear..."
            )

            renomear = wait.until(
                EC.presence_of_element_located(
                    (
                        By.ID,
                        "dms-fe-legacy-components-client-documents-rename-button"
                    )
                )
            )

            logger.info(
                "Botão Renomear localizado."
            )

            # garantir visível
            driver.execute_script("""
                arguments[0].scrollIntoView({
                    block: 'center'
                });
            """, renomear)

            time.sleep(0.5)

            logger.info(
                "Clicando em Renomear..."
            )

            # clique REAL no Angular
            driver.execute_script("""
                arguments[0].dispatchEvent(
                    new MouseEvent('mousedown', {
                        bubbles: true
                    })
                );

                arguments[0].dispatchEvent(
                    new MouseEvent('mouseup', {
                        bubbles: true
                    })
                );

                arguments[0].click();
            """, renomear)

            logger.info(
                "Renomear clicado."
            )

            time.sleep(1)

            # preencher nome
            campo_nome = wait.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//input"
                    )
                )
            )

            campo_nome.clear()
            campo_nome.send_keys(new_name)

            logger.info(
                f"Novo nome preenchido: {new_name}"
            )

            # ==========================================
            # CONFIRMAR RENOMEAÇÃO
            # ==========================================

            logger.info(
                "Procurando botão final Renomear..."
            )

            confirmar = wait.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//button[@ng-click='renameFileRequest()']"
                    )
                )
            )

            logger.info(
                "Botão final Renomear localizado."
            )

            # garantir visível
            driver.execute_script("""
                arguments[0].scrollIntoView({
                    block: 'center'
                });
            """, confirmar)

            time.sleep(0.5)

            logger.info(
                "Clicando no botão final..."
            )

            # clique mais confiável
            driver.execute_script("""
                arguments[0].dispatchEvent(
                    new MouseEvent('mousedown', {
                        bubbles: true
                    })
                );

                arguments[0].dispatchEvent(
                    new MouseEvent('mouseup', {
                        bubbles: true
                    })
                );

                arguments[0].click();
            """, confirmar)

            logger.info(
                "Botão final Renomear clicado."
            )

            logger.info(
                "Aguardando janela de renomear fechar..."
            )

            # espera modal de renomear desaparecer
            WebDriverWait(driver, 60).until_not(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//button[@ng-click='renameFileRequest()']"
                    )
                )
            )

            logger.info(
                "Janela de renomear fechada."
            )

            logger.info(
                "Aguardando nome do arquivo atualizar na lista..."
            )

            nome_antigo = os.path.basename(file_path)

            timeout = 60
            inicio = time.time()

            nome_atualizado = False

            while time.time() - inicio < timeout:

                try:
                    textos = driver.find_elements(
                        By.XPATH,
                        "//a"
                    )

                    nomes_visiveis = [
                        el.text.strip()
                        for el in textos
                        if el.is_displayed()
                        and el.text.strip()
                    ]

                    # novo nome apareceu
                    if any(new_name in n for n in nomes_visiveis):

                        logger.info(
                            f"Nome atualizado encontrado: "
                            f"{new_name}"
                        )

                        nome_atualizado = True
                        break

                    # nome antigo sumiu
                    if not any(
                        nome_antigo in n
                        for n in nomes_visiveis
                    ):

                        logger.info(
                            "Nome antigo sumiu da lista."
                        )

                        nome_atualizado = True
                        break

                except:
                    pass

                time.sleep(1)

            if not nome_atualizado:
                raise Exception(
                    "Nome do arquivo não atualizou."
                )

            logger.info(
                "Renomeação confirmada."
            )

            # opcional: pequeno delay extra
            time.sleep(1)

        except Exception as e:

            logger.error(
                f"Erro ao renomear documento: {e}"
            )

            return False, (
                "Erro na renomeação."
            )


        # ==========================================
        # DEFINIR DATA DE VENCIMENTO
        # ==========================================

        logger.info(
            "Definindo data de vencimento..."
        )

        try:

            logger.info(
                "Localizando botão Gerenciar..."
            )

            gerenciar = wait.until(
                EC.presence_of_element_located(
                    (
                        By.ID,
                        "dms-fe-legacy-components-client-documents-manage-docs-menu-button"
                    )
                )
            )

            logger.info(
                "Botão Gerenciar localizado."
            )

            driver.execute_script("""
                arguments[0].scrollIntoView({
                    block:'center'
                });
            """, gerenciar)

            time.sleep(0.5)

            logger.info(
                "Clicando em Gerenciar novamente..."
            )

            driver.execute_script("""
                arguments[0].dispatchEvent(
                    new MouseEvent('mousedown', {
                        bubbles: true
                    })
                );

                arguments[0].dispatchEvent(
                    new MouseEvent('mouseup', {
                        bubbles: true
                    })
                );

                arguments[0].click();
            """, gerenciar)

            logger.info(
                "Botão Gerenciar clicado novamente."
            )

            time.sleep(1)

            logger.info(
                "Procurando botão 'Definir data de vencimento'..."
            )

            vencimento = None

            for tentativa in range(15):

                logger.info(
                    f"Scroll dropdown tentativa {tentativa + 1}"
                )

                try:
                    # tenta localizar o botão
                    botoes = driver.find_elements(
                        By.XPATH,
                        "//a[contains(normalize-space(),"
                        "'Definir data de vencimento')]"
                    )

                    for botao in botoes:

                        try:
                            if botao.is_displayed():

                                vencimento = botao

                                logger.info(
                                    "Botão encontrado."
                                )

                                break

                        except:
                            pass

                    if vencimento:
                        break

                    # scroll dentro do menu dropdown
                    driver.execute_script("""
                        const menus =
                            document.querySelectorAll(
                                '.dropdown-menu'
                            );

                        for (const menu of menus) {

                            if (
                                menu.offsetParent !== null
                            ) {
                                menu.scrollTop += 250;
                            }
                        }
                    """)

                    time.sleep(0.8)

                except Exception as e:

                    logger.info(
                        f"Falha tentativa "
                        f"{tentativa+1}: {e}"
                    )

            if vencimento is None:
                raise Exception(
                    "Botão 'Definir data de vencimento' "
                    "não encontrado."
                )

            # garantir visível
            driver.execute_script("""
                arguments[0].scrollIntoView({
                    block:'center'
                });
            """, vencimento)

            time.sleep(0.5)

            logger.info(
                "Clicando em "
                "'Definir data de vencimento'..."
            )

            # clique JS igual ao Renomear
            driver.execute_script("""
                arguments[0].dispatchEvent(
                    new MouseEvent('mousedown', {
                        bubbles: true
                    })
                );

                arguments[0].dispatchEvent(
                    new MouseEvent('mouseup', {
                        bubbles: true
                    })
                );

                arguments[0].click();
            """, vencimento)

            logger.info(
                "Botão Definir data "
                "de vencimento clicado."
            )

            time.sleep(2)

            logger.info(
                "Procurando campo da data..."
            )

            campo_data = wait.until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//input[contains(@ng-model,'dueDate') or @placeholder='dd/mm/aaaa' or @type='text']"
                    )
                )
            )

            logger.info(
                "Verificando checkbox do calendário..."
            )

            try:

                checkbox = wait.until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "//input[@type='checkbox']"
                        )
                    )
                )

                esta_marcada = checkbox.is_selected()

                logger.info(
                    f"Checkbox marcada? "
                    f"{esta_marcada}"
                )

                if not esta_marcada:

                    driver.execute_script("""
                        arguments[0].click();
                    """, checkbox)

                    logger.info(
                        "Checkbox marcada."
                    )

                    time.sleep(0.5)

                else:

                    logger.info(
                        "Checkbox já estava marcada."
                    )

            except Exception as e:

                logger.warning(
                    f"Erro ao marcar checkbox: {e}"
                )

            logger.info(
                "Campo da data localizado."
            )

            # scroll até o campo
            driver.execute_script("""
                arguments[0].scrollIntoView({
                    block: 'center'
                });
            """, campo_data)

            time.sleep(0.5)

            # clicar no campo
            driver.execute_script(
                "arguments[0].click();",
                campo_data
            )

            time.sleep(0.3)

            # limpar corretamente
            driver.execute_script("""
                arguments[0].value = '';
                arguments[0].dispatchEvent(
                    new Event('input', { bubbles: true })
                );
            """, campo_data)

            time.sleep(0.2)

            # preencher via JS (mais estável no Angular)
            driver.execute_script("""
                arguments[0].value = arguments[1];

                arguments[0].dispatchEvent(
                    new Event('input', { bubbles: true })
                );

                arguments[0].dispatchEvent(
                    new Event('change', { bubbles: true })
                );

                arguments[0].dispatchEvent(
                    new Event('blur', { bubbles: true })
                );
            """, campo_data, due_date)

            logger.info(
                f"Data preenchida: {due_date}"
            )

            time.sleep(1)

            confirmar = wait.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//button[contains(., 'Salvar') "
                        "or contains(., 'Confirmar')]"
                    )
                )
            )

            driver.execute_script("""
                arguments[0].click();
            """, confirmar)

            logger.info(
                "Data de vencimento definida."
            )

            time.sleep(3)

        except Exception as e:

            logger.error(
                f"Erro ao definir vencimento: {e}"
            )

            return False, (
                "Erro ao definir vencimento."
            )


        logger.info(
            "Processo concluído com sucesso."
        )

        return True, "Upload concluído."

    except Exception as e:
        logger.critical(f"Erro crítico na automação do ONVIO: {e}", exc_info=True)
        return False, f"Erro crítico: {str(e)}"
    finally:
        # O driver não deve ser fechado aqui se a intenção é reutilizar a sessão de depuração.
        # driver.quit() 
        pass
