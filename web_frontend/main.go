package main

import (
	"bytes"
	"fmt"
	"html/template"
	"io"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"

	"github.com/labstack/echo/v4"
	"github.com/sirupsen/logrus"
)

/*--- log part ---*/
var log *logrus.Logger

type MyFormatter struct{}

func (m *MyFormatter) Format(entry *logrus.Entry) ([]byte, error) {
	var b *bytes.Buffer
	if entry.Buffer != nil {
		b = entry.Buffer
	} else {
		b = &bytes.Buffer{}
	}

	timestamp := entry.Time.Format("2006-01-02 15:04:05")

	var logLevel string
	switch entry.Level {
	case logrus.DebugLevel:
		logLevel = "\033[1;35mDEBUG\033[0m" // 使用紫色上色
	case logrus.InfoLevel:
		logLevel = "\033[1;32mINFO\033[0m" // 使用綠色上色
	case logrus.WarnLevel:
		logLevel = "\033[1;33mWARN\033[0m" // 使用黃色上色
	case logrus.ErrorLevel:
		logLevel = "\033[1;31mERROR\033[0m" // 使用紅色上色
	case logrus.FatalLevel:
		logLevel = "\033[1;31mFATAL\033[0m" // 使用紅色上色
	case logrus.PanicLevel:
		logLevel = "\033[1;31mPANIC\033[0m" // 使用紅色上色
	default:
		logLevel = fmt.Sprintf("[%s]", entry.Level)
	}

	var newLog string

	//HasCaller()為true才會有調用信息
	if entry.HasCaller() {
		fName := filepath.Base(entry.Caller.File)
		newLog = fmt.Sprintf("[%s][%s][%s:%d] %s\n",
			logLevel, timestamp, fName, entry.Caller.Line, entry.Message)
	} else {
		newLog = fmt.Sprintf("[%s][%s] %s\n", logLevel, timestamp, entry.Message)
	}

	b.WriteString(newLog)
	return b.Bytes(), nil
}

func initLogger() *logrus.Logger {
	// 創建一個新的 logrus 實例
	logger := logrus.New()

	// 設定 logrus 日誌紀錄格式
	logger.SetFormatter(&MyFormatter{})

	// 設定 logrus 輸出位置為 os.Stderr (終端輸出)
	logger.SetOutput(os.Stderr)

	// 設定報告呼叫函式的行數
	logger.SetReportCaller(true)

	return logger
}

/*--- log part ---*/

/*--- template part ---*/
// 固定用法: 宣告TemplateRegistry這個struct，等等需定義.Render()這個method
type TemplateRegistry struct {
	templates map[string]*template.Template
}

// TemplateRegistry的一個method，描述了模板實際的渲染方式
func (t *TemplateRegistry) Render(w io.Writer, name string, data interface{},
	c echo.Context) error {
	return t.templates[name].ExecuteTemplate(w, name, data)
}

/*--- template part ---*/

func storeTempImages(c echo.Context, name string, store_position string) string {
	file, err := c.FormFile(name)
	if err != nil {
		return "無法取得上傳檔案:" + err.Error()
	}

	// 開啟要寫入的檔案
	uploadedFile, err := file.Open()
	if err != nil {
		// 處理錯誤
		fmt.Println("無法開啟要寫入的檔案:", err)
		return "無法開啟要寫入的檔案:" + err.Error()
	}
	defer uploadedFile.Close()

	// 建立目標檔案
	targetFile, err := os.Create(store_position)
	if err != nil {
		return "無法建立目標檔案:" + err.Error()
	}
	defer targetFile.Close()

	// 將圖片內容寫入目標檔案
	_, err = io.Copy(targetFile, uploadedFile)
	if err != nil {
		return "無法寫入目標檔案:" + err.Error()
	}

	return ""
}

func decodeLSB_Text_Prediction(output string) string {
	reg := regexp.MustCompile(`\$\d+\.\d+\$`) // 用正則表達式找出 $xxx.xx$ 的小數字串
	match := reg.FindString(output)
	fmt.Println("match:", match)
	return match[1 : len(match)-1]
}

func Detection(c echo.Context) error {
	if c.Request().Method == "GET" {
		log.Info("switch to /detection (GET)")

		return c.File("views/detection.html")
	} else if c.Request().Method == "POST" {
		log.Info("switch to /detection (POST)")

		err_str := storeTempImages(c, "image", "static/images/userUpload.png")
		if err_str != "" {
			log.Error(err_str)

			return c.String(200, err_str)
		}

		cmd := exec.Command("python", "../web_backend/LSB_Text_Predict.py")
		output, err := cmd.CombinedOutput()
		if err != nil {
			log.Error("執行 LSB.py 時發生錯誤:", err)
		}
		log.Info("LSB_Text_Prediction.py 輸出:", string(output))

		LSB_Text_Prediction := decodeLSB_Text_Prediction(string(output))
		log.Info("LSB_Text_Prediction:", LSB_Text_Prediction)

		cmd = exec.Command("python", "../web_backend/LSB_QRcode_Predict.py")
		output, err = cmd.CombinedOutput()
		if err != nil {
			log.Error("執行 LSB_QRcode_Predict.py 時發生錯誤:", err)
		}
		log.Info("LSB_QRcode_Predict.py 輸出:", string(output))

		LSB_QRcode_Prediction := decodeLSB_Text_Prediction(string(output))
		log.Info("LSB_QRcode_Prediction:", LSB_QRcode_Prediction)

		temp := map[string]interface{}{}
		temp["LSB_Text_Prediction"] = LSB_Text_Prediction
		temp["LSB_QRcode_Prediction"] = LSB_QRcode_Prediction
		return c.Render(http.StatusOK, "detection_result", temp)

		//return c.Redirect(http.StatusFound, "/detection_result")
	}

	return c.File("views/detection.html")
}

func Detection_Result(c echo.Context) error {
	if c.Request().Method == "GET" {
		log.Info("switch to /detection_result (GET)")

		return c.File("views/detection_result.html")
	}

	return c.File("views/404NotFound.html")
}

func Make(c echo.Context) error {
	if c.Request().Method == "GET" {
		log.Info("switch to /make (GET)")

		return c.File("views/make.html")
	} else if c.Request().Method == "POST" {
		log.Info("switch to /make (POST)")

		if c.FormValue("type") == "LSB隱寫文字" {
			err_str := storeTempImages(c, "image", "static/images/userUpload.png")
			if err_str != "" {
				log.Error(err_str)

				return c.String(200, err_str)
			}

			log.Info("reveive hidden text:", c.FormValue("hidden_text"))

			hidden_text := c.FormValue("hidden_text")
			cmd := exec.Command("python", "../web_backend/LSB_Text.py", hidden_text)
			output, err := cmd.CombinedOutput()
			if err != nil {
				log.Error("執行 LSB.py 時發生錯誤:", err)
			}
			log.Info("LSB.py 輸出:", string(output))

		} else if c.FormValue("type") == "LSB QRcode" {
			err_str := storeTempImages(c, "image1", "static/images/userUpload.png")
			if err_str != "" {
				log.Error(err_str)

				return c.String(200, err_str)
			}
			err_str = storeTempImages(c, "image2", "static/images/userUpload_QRcode.png")
			if err_str != "" {
				log.Error(err_str)

				return c.String(200, err_str)
			}

			cmd := exec.Command("python", "../web_backend/LSB_QRcode.py")
			output, err := cmd.CombinedOutput()
			if err != nil {
				log.Error("執行 LSB_QRcode.py 時發生錯誤:", err)
			}
			log.Info("LSB_QRcode.py 輸出:", string(output))
		}

		log.Info("執行完畢")
		return c.Redirect(http.StatusFound, "/make_result")
	}

	return c.File("views/404NotFound.html")
}

func Make_Result(c echo.Context) error {
	if c.Request().Method == "GET" {
		log.Info("switch to /make_result (GET)")

		return c.File("views/make_result.html")
	}

	return c.File("views/404NotFound.html")
}

func main() {
	log = initLogger()

	e := echo.New()
	e.Static("/static", "static")

	/*--- template part ---*/
	templates := make(map[string]*template.Template)
	templates["detection_result"] = template.Must(template.ParseFiles("views/detection_result.html"))
	e.Renderer = &TemplateRegistry{ //連結echo框架跟TemplateRegistry struct
		templates: templates,
	}
	/*--- template part ---*/

	e.GET("/", Detection)
	e.GET("/detection", Detection)
	e.POST("/detection", Detection)
	e.GET("/detection_result", Detection_Result)
	e.GET("/make", Make)
	e.POST("/make", Make)
	e.GET("/make_result", Make_Result)

	e.Start(":8000")
}
